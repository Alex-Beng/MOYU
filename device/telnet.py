# -*- coding: utf-8 -*-
import copy
import math
import sys
import logging
from code import InteractiveConsole
from io import StringIO

logger = logging.getLogger(__name__)

DONT     = bytes([254])
DO       = bytes([253])
WILL     = bytes([251])
WONT     = bytes([252])
ECHO     = bytes([1])
SGA      = bytes([3])
LINEMODE = bytes([34])
SUB      = bytes([26])
SOH      = bytes([1])
TB       = bytes([23])
ESC      = bytes([27])
BSP      = bytes([8])
DEL      = bytes([127])
SE       = bytes([240])
NOP      = bytes([241])
SB       = bytes([250])
TAB      = bytes([9])
BELL     = bytes([7])
NOOPT    = bytes([0])
TTYPE    = bytes([24])
IS       = bytes([0])
SEND     = bytes([1])
IAC      = bytes([255])
DEFAULT  = -1

HISTORY_MAX        = 50
EDIT_HISTORY_MAX   = 30
AUTOCOMPLETE_WORLDS_INLINE  = 4
AUTOCOMPLETE_DISPLAY_MAX    = 20
AUTOCOMPLETE_MAX_LINES      = math.ceil(AUTOCOMPLETE_DISPLAY_MAX / AUTOCOMPLETE_WORLDS_INLINE)
AUTOCOMPLETE_WORD_SPACING   = 5
QUIT_FLAGS = {'quit', 'quit()', 'exit', 'exit()'}


class _Render:
    REVERSE = b'\x1b[7m'
    RESET   = b'\x1b[0m'
    DEL_CH  = b'\x1b[K'
    LEFT    = b'\x1b[D'
    RIGHT   = b'\x1b[C'


def _is_name_byte(b: bytes) -> bool:
    return b.isalpha() or b.isdigit() or b == b'_'


def _common_prefix(lst):
    if not lst:
        return ''
    s1, s2 = min(lst), max(lst)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


def _candidates(ctx_obj, prefix: str, global_keys: list) -> list:
    if ctx_obj is not None:
        words = list(dir(ctx_obj))
    else:
        words = list(global_keys)
    if prefix == '':
        return [w for w in words if not w.startswith('__')]
    return [w for w in words if w.startswith(prefix)]


class TelnetHandler:
    USEFUL_CMDS = frozenset([DO, DONT, WILL, WONT])
    DOACK  = {ECHO: WILL, SGA: WILL}
    WILLACK = {ECHO: DONT, SGA: DO, LINEMODE: DONT}

    def __init__(self, conn: 'TelnetConnection'):
        self.conn = conn
        self.DOOPTS   = {}
        self.WILLOPTS = {}

        self.current_line: list  = []
        self.render_line:  list  = []
        self.cursor_ptr    = 0
        self.last_current_line: list = []
        self.last_cursor_ptr = 0
        self.select_ptr    = 0

        self.edit_history: list  = []
        self.just_edit     = False
        self.add_to_edit_history()

        self.history: list = []
        self.history_ptr   = -1
        self.candidate_words: list = []
        self.tab_last_line = None

        self.sb        = 0
        self.sbdataq   = b''
        self.iac_sq    = b''

        self.OPERATION_CMD = {
            b'\x1b[A':    self.handle_up,
            b'\x1b[2A':   self.handle_up,
            b'\x1b[1;2A': self.handle_up,
            b'\x1b[5A':   self.handle_up,
            b'\x1b[1;5A': self.handle_up,
            b'\x1b[B':    self.handle_down,
            b'\x1b[2B':   self.handle_down,
            b'\x1b[1;2B': self.handle_down,
            b'\x1b[5B':   self.handle_down,
            b'\x1b[1;5B': self.handle_down,
            b'\x1b[D':    self.handle_left,
            b'\x1b[2D':   self.handle_shift_left,
            b'\x1b[1;2D': self.handle_shift_left,
            b'\x1b[5D':   self.handle_ctrl_left,
            b'\x1b[1;5D': self.handle_ctrl_left,
            b'\x1b[C':    self.handle_right,
            b'\x1b[2C':   self.handle_shift_right,
            b'\x1b[1;2C': self.handle_shift_right,
            b'\x1b[5C':   self.handle_ctrl_right,
            b'\x1b[1;5C': self.handle_ctrl_right,
            b'\x1b[H':    self.handle_home,
            b'\x1b[F':    self.handle_end,
            b'\x1b[3~':   self.handle_delete,
            b'\x1b[1~':   self.handle_home,
            b'\x1b[4~':   self.handle_end,
            b'\x1bOD':    self.handle_ctrl_left,
            b'\x1bOC':    self.handle_ctrl_right,
            b'\x1b[1;5H': self.handle_home,
            b'\x1b[1;5F': self.handle_end,
            b'\x1b[2H':   self.handle_shift_home,
            b'\x1b[2F':   self.handle_shift_end,
            b'\x1b[1;2~': self.handle_shift_home,
            b'\x1b[4;2~': self.handle_shift_end,
            b'\x1b[1;6D': self.handle_ctrl_shift_left,
            b'\x1b[1;6C': self.handle_ctrl_shift_right,
        }
        self.CHAR_HANDLER = {
            ESC: self.handle_esc,
            BSP: self.handle_backspace,
            DEL: self.handle_backspace,
            TAB: self.handle_tab,
            SUB: self.handle_sub,
            SOH: self.handle_soh,
            TB:  self.handle_tb,
            SGA: lambda r, i: 1,
            DEFAULT: self.handle_default_char,
        }
        self.CMD_HANDLER = {
            NOP:  self.handle_nop,
            WILL: self.handle_will_wont,
            WONT: self.handle_will_wont,
            DO:   self.handle_do_dont,
            DONT: self.handle_do_dont,
            SE:   self.handle_se,
            SB:   self.handle_sb,
        }
        self._setup()

    def _setup(self):
        for k in self.DOACK:
            self._send_cmd(self.DOACK[k], k)
        for k in self.WILLACK:
            self._send_cmd(self.WILLACK[k], k)

    def handle_input(self, data: bytes):
        if b'\r\n' in data:
            lines = data.split(b'\r\n')
            complete = data.endswith(b'\r\n')
            if complete and lines and lines[-1] == b'':
                lines = lines[:-1]
        elif b'\r\x00' in data:
            lines = data.split(b'\r\x00')
            complete = data.endswith(b'\r\x00')
            if complete and lines and lines[-1] == b'':
                lines = lines[:-1]
        else:
            lines = [data]
            complete = False

        for i, raw in enumerate(lines):
            self._process_raw(raw)
            if complete or i < len(lines) - 1:
                if self.current_line:
                    self.history.append(list(self.current_line))
                    self.history_ptr = len(self.history)
                else:
                    self.current_line.append(b'\n')
                line_bytes = b''.join(self.current_line)
                self._write(b'\r\n')
                self.conn.receive_line(line_bytes)
                self.current_line = []
                self.cursor_ptr   = 0
                self.render_line  = []
                self.last_current_line = []
                self.last_cursor_ptr   = 0
                while len(self.history) > HISTORY_MAX:
                    self.history.pop(0)
                    self.history_ptr -= 1

    def _process_raw(self, raw: bytes):
        idx = 0
        while idx < len(raw):
            ch = bytes([raw[idx]])
            if ch == IAC or self.iac_sq or self.sb:
                idx += self._process_cmd(raw[idx:])
                continue
            if ch in self.CHAR_HANDLER:
                offset = self.CHAR_HANDLER[ch](raw, idx)
                if ch != TAB:
                    self.candidate_words = []
                    self.tab_last_line   = None
            else:
                self.candidate_words = []
                self.tab_last_line   = None
                offset = self.CHAR_HANDLER[DEFAULT](ch)
            idx += offset

    def _process_cmd(self, data: bytes) -> int:
        idx = 0
        while idx < len(data):
            c = bytes([data[idx]])
            if not self.iac_sq:
                if c == IAC:
                    self.iac_sq += c
                elif self.sb:
                    self.sbdataq += c
                idx += 1
                continue
            if len(self.iac_sq) == 1:
                if c in self.USEFUL_CMDS:
                    self.iac_sq += c
                    idx += 1
                    continue
                self.iac_sq = b''
                if c == SB:
                    self.sb = 1
                    self.sbdataq = b''
                elif c == SE:
                    self.sb = 0
                    if SE in self.CMD_HANDLER:
                        self.CMD_HANDLER[SE](SE, NOOPT)
                idx += 1
                break
            if len(self.iac_sq) == 2:
                cmd = self.iac_sq[1:2]
                self.iac_sq = b''
                if cmd in self.USEFUL_CMDS and cmd in self.CMD_HANDLER:
                    self.CMD_HANDLER[cmd](cmd, c)
                idx += 1
                break
        return idx

    def _navi(self, cmd, opt=None):
        self._send_cmd(cmd, opt)

    def handle_nop(self, cmd, opt):
        pass

    def handle_will_wont(self, cmd, opt):
        ack = self.WILLACK.get(opt, DONT)
        self._send_cmd(ack, opt)

    def handle_do_dont(self, cmd, opt):
        ack = self.DOACK.get(opt, WONT)
        self._send_cmd(ack, opt)

    def handle_se(self, cmd, opt):
        pass

    def handle_sb(self, cmd, opt):
        pass

    def handle_up(self):
        if self.history_ptr > 0:
            self.history_ptr -= 1
            self.current_line = copy.deepcopy(self.history[self.history_ptr])
            self.cursor_ptr = len(self.current_line)
            self.select_ptr = self.cursor_ptr
            self._render()
        else:
            self._bell()

    def handle_down(self):
        if self.history_ptr < len(self.history):
            self.history_ptr += 1
            if self.history_ptr >= len(self.history):
                self.current_line = []
            else:
                self.current_line = copy.deepcopy(self.history[self.history_ptr])
            self.cursor_ptr = len(self.current_line)
            self.select_ptr = self.cursor_ptr
            self._render()
        else:
            self._bell()

    def handle_left(self):
        if self.cursor_ptr > 0:
            if self.select_ptr != self.cursor_ptr:
                self.cursor_ptr = min(self.select_ptr, self.cursor_ptr)
                self.select_ptr = self.cursor_ptr
            else:
                self.cursor_ptr -= 1
                self.select_ptr  = self.cursor_ptr
            self._render()
        else:
            if self.select_ptr != self.cursor_ptr:
                self.select_ptr = self.cursor_ptr
                self._render()
            else:
                self._bell()

    def handle_right(self):
        if self.cursor_ptr < len(self.current_line):
            if self.select_ptr != self.cursor_ptr:
                self.cursor_ptr = max(self.select_ptr, self.cursor_ptr)
                self.select_ptr = self.cursor_ptr
            else:
                self.cursor_ptr += 1
                self.select_ptr  = self.cursor_ptr
            self._render()
        else:
            if self.select_ptr != self.cursor_ptr:
                self.select_ptr = self.cursor_ptr
                self._render()
            else:
                self._bell()

    def handle_shift_left(self):
        if self.cursor_ptr > 0:
            self.cursor_ptr -= 1
            self._render()
        else:
            self._bell()

    def handle_shift_right(self):
        if self.cursor_ptr < len(self.current_line):
            self.cursor_ptr += 1
            self._render()
        else:
            self._bell()

    def handle_home(self):
        if self.cursor_ptr > 0 or self.select_ptr != self.cursor_ptr:
            self.cursor_ptr = 0
            self.select_ptr = 0
            self._render()
        else:
            self._bell()

    def handle_end(self):
        end = len(self.current_line)
        if self.cursor_ptr < end or self.select_ptr != self.cursor_ptr:
            self.cursor_ptr = end
            self.select_ptr = end
            self._render()
        else:
            self._bell()

    def handle_shift_home(self):
        if self.cursor_ptr > 0:
            self.cursor_ptr = 0
            self._render()
        else:
            self._bell()

    def handle_shift_end(self):
        if self.cursor_ptr < len(self.current_line):
            self.cursor_ptr = len(self.current_line)
            self._render()
        else:
            self._bell()

    def handle_ctrl_left(self):
        if self.cursor_ptr > 0:
            flag = _is_name_byte(self.current_line[self.cursor_ptr - 1])
            t = 0
            for i in range(self.cursor_ptr - 1, 0, -1):
                if flag ^ _is_name_byte(self.current_line[i]):
                    t = i + 1
                    break
            self.cursor_ptr = t
            self.select_ptr = t
            self._render()
        else:
            self._bell()

    def handle_ctrl_right(self):
        n = len(self.current_line)
        if self.cursor_ptr < n:
            flag = _is_name_byte(self.current_line[self.cursor_ptr])
            t = n
            for i in range(self.cursor_ptr, n):
                if flag ^ _is_name_byte(self.current_line[i]):
                    t = i
                    break
            self.cursor_ptr = t
            self.select_ptr = t
            self._render()
        else:
            self._bell()

    def handle_ctrl_shift_left(self):
        self.handle_ctrl_left()

    def handle_ctrl_shift_right(self):
        self.handle_ctrl_right()

    def handle_delete(self):
        if self.select_ptr == self.cursor_ptr:
            if self.cursor_ptr == len(self.current_line):
                self._bell()
                return
            del self.current_line[self.cursor_ptr]
        elif self.select_ptr > self.cursor_ptr:
            del self.current_line[self.cursor_ptr:self.select_ptr]
            self.select_ptr = self.cursor_ptr
        else:
            del self.current_line[self.select_ptr:self.cursor_ptr]
            self.cursor_ptr = self.select_ptr
        self._render()
        self.add_to_edit_history()

    def handle_default_char(self, ch: bytes):
        self.current_line.insert(self.cursor_ptr, ch)
        self.cursor_ptr += 1
        self.select_ptr  = self.cursor_ptr
        self._render()
        self.add_to_edit_history()
        return 1

    def add_to_edit_history(self):
        self.edit_history.append((self.cursor_ptr, list(self.current_line), self.select_ptr))
        if len(self.edit_history) > EDIT_HISTORY_MAX:
            self.edit_history = self.edit_history[-EDIT_HISTORY_MAX:]
        self.just_edit = True

    def handle_esc(self, raw: bytes, idx: int):
        for length in (6, 5, 4, 3):
            seq = raw[idx:idx + length]
            if seq in self.OPERATION_CMD:
                self.OPERATION_CMD[seq]()
                return length
        return 3

    def handle_backspace(self, raw: bytes, idx: int):
        if self.select_ptr == self.cursor_ptr:
            if self.cursor_ptr == 0:
                self._bell()
                return 1
            self.cursor_ptr -= 1
            self.select_ptr  = self.cursor_ptr
            del self.current_line[self.cursor_ptr]
        elif self.select_ptr > self.cursor_ptr:
            del self.current_line[self.cursor_ptr:self.select_ptr]
            self.select_ptr = self.cursor_ptr
        else:
            del self.current_line[self.select_ptr:self.cursor_ptr]
            self.cursor_ptr = self.select_ptr
        self._render()
        self.add_to_edit_history()
        return 1

    def _get_context(self):
        cur = self.cursor_ptr
        for i in range(cur - 1, -1, -1):
            if _is_name_byte(self.current_line[i]):
                cur = i
            else:
                break
        prefix = b''.join(self.current_line[cur:self.cursor_ptr])
        if cur <= 0 or self.current_line[cur - 1] != b'.':
            return b'', prefix
        dot = cur - 1
        sq = par = 0
        ctx_start = dot
        for i in range(dot - 1, -1, -1):
            c = self.current_line[i]
            if c == b'(':
                if par == 0:
                    break
                par -= 1
            elif c == b')':
                par += 1
            elif c == b'[':
                if sq == 0:
                    break
                sq -= 1
            elif c == b']':
                sq += 1
            elif _is_name_byte(c) or c == b'.':
                pass
            else:
                if par == 0 and sq == 0:
                    break
            ctx_start = i
        return b''.join(self.current_line[ctx_start:dot]), prefix

    def _complete_insert(self, suffix: str):
        for c in suffix:
            self.current_line.insert(self.cursor_ptr, c.encode())
            self.cursor_ptr += 1
        self.select_ptr = self.cursor_ptr
        self._render()
        self.add_to_edit_history()

    def handle_tab(self, raw: bytes, idx: int):
        if self.current_line != self.tab_last_line:
            self.tab_last_line = list(self.current_line)
            ctx_bytes, prefix_bytes = self._get_context()
            prefix = prefix_bytes.decode('utf-8', errors='replace')
            ctx_str = ctx_bytes.decode('utf-8', errors='replace')

            ctx_obj = None
            if ctx_str:
                try:
                    ctx_obj = eval(ctx_str, self.conn.console.locals)
                except Exception:
                    pass

            try:
                global_keys = list(self.conn.console.locals.keys())
            except Exception:
                global_keys = []

            self.candidate_words = _candidates(ctx_obj, prefix, global_keys)

            if not self.candidate_words:
                self._info("No candidates")
                self._bell()
            elif len(self.candidate_words) == 1:
                word = self.candidate_words[0]
                if word == prefix:
                    full = f'{ctx_str}.{prefix}' if ctx_str else prefix
                    try:
                        obj = eval(full, self.conn.console.locals)
                        self._complete_insert('(' if callable(obj) else '.')
                    except Exception:
                        self._complete_insert('.')
                else:
                    self._complete_insert(word[len(prefix):])
            else:
                lcp = _common_prefix(self.candidate_words)
                if lcp == prefix:
                    self._show_candidates(self.candidate_words)
                else:
                    self._complete_insert(lcp[len(prefix):])
        else:
            if len(self.candidate_words) > 1:
                self._show_candidates(self.candidate_words)
            else:
                self._bell()
        return 1

    def _info(self, msg: str):
        self._write(b'\r\n--- ' + msg.encode() + b'\r\n')
        self.conn.send_ps()
        self.last_current_line = []
        self.last_cursor_ptr   = 0
        self.render_line       = []
        self._render()

    def _show_candidates(self, words: list):
        self._write(b'\r\n')
        display = words[:AUTOCOMPLETE_DISPLAY_MAX]
        exceeded = len(words) > AUTOCOMPLETE_DISPLAY_MAX
        w = max(len(x) for x in display) + AUTOCOMPLETE_WORD_SPACING
        for i in range(0, len(display), AUTOCOMPLETE_WORLDS_INLINE):
            row = display[i:i + AUTOCOMPLETE_WORLDS_INLINE]
            self._write(b'  ' + b''.join(x.encode().ljust(w) for x in row) + b'\r\n')
        if exceeded:
            self._write(f'--- {len(words)} candidates, showing {AUTOCOMPLETE_DISPLAY_MAX} ---\r\n'.encode())
        self.conn.send_ps()
        self.last_current_line = []
        self.last_cursor_ptr   = 0
        self.render_line       = []
        self._render()

    def handle_sub(self, raw: bytes, idx: int):
        if self.just_edit and self.edit_history:
            self.edit_history.pop()
            self.just_edit = False
        if self.edit_history:
            self.cursor_ptr, self.current_line, self.select_ptr = self.edit_history[-1]
            self.current_line = list(self.current_line)
            self.edit_history.pop()
            self._render()
        else:
            self._bell()
        return 1

    def handle_soh(self, raw: bytes, idx: int):
        if self.current_line:
            self.cursor_ptr = len(self.current_line)
            self.select_ptr = 0
            self._render()
        else:
            self._bell()
        return 1

    def handle_tb(self, raw: bytes, idx: int):
        if self.cursor_ptr > 0:
            flag = _is_name_byte(self.current_line[self.cursor_ptr - 1])
            t = 0
            for i in range(self.cursor_ptr - 1, 0, -1):
                if flag ^ _is_name_byte(self.current_line[i]):
                    t = i + 1
                    break
            if self.select_ptr == self.cursor_ptr:
                del self.current_line[t:self.cursor_ptr]
                self.cursor_ptr = t
                self.select_ptr = t
            else:
                lo, hi = min(self.cursor_ptr, self.select_ptr), max(self.cursor_ptr, self.select_ptr)
                del self.current_line[lo:hi]
                self.cursor_ptr = lo
                self.select_ptr = lo
            self._render()
            self.add_to_edit_history()
        return 1

    def _render(self):
        last = list(self.render_line)
        self.render_line = list(self.current_line)

        sp, cp = self.select_ptr, self.cursor_ptr
        if sp == cp:
            rcp = cp
            self.render_line.extend([_Render.LEFT] * (len(self.render_line) - rcp))
        elif sp > cp:
            rcp = cp + 2
            self.render_line.insert(cp, _Render.REVERSE)
            self.render_line.insert(sp + 1, _Render.RESET)
            self.render_line.extend([_Render.LEFT] * (len(self.render_line) - rcp))
        else:
            rcp = cp + 2
            self.render_line.insert(sp, _Render.REVERSE)
            self.render_line.insert(cp + 1, _Render.RESET)
            self.render_line.extend([_Render.LEFT] * (len(self.render_line) - rcp))

        same = -1
        for i in range(min(len(self.render_line), len(last))):
            if self.render_line[i] != last[i]:
                break
            if self.render_line[i] in (_Render.REVERSE, _Render.RESET):
                break
            if last[i] in (_Render.REVERSE, _Render.RESET):
                break
            same = i
        diff = same + 1

        def _valid(lst):
            return [x for x in lst if x not in (_Render.REVERSE, _Render.RESET, _Render.LEFT)]

        if diff >= len(last):
            self._write(b''.join(self.render_line[diff:]))
        elif diff >= len(self.render_line):
            if last[diff] == _Render.LEFT:
                self._write(_Render.RIGHT * (len(last) - diff))
            else:
                v = _valid(last[diff:])
                lefts = [x for x in last[diff:] if x == _Render.LEFT]
                self._write(_Render.RIGHT * len(lefts))
                self._write((_Render.LEFT + _Render.DEL_CH) * len(v))
        else:
            v = _valid(last[diff:])
            self._write(_Render.RIGHT * (len(self.last_current_line) - self.last_cursor_ptr))
            self._write((_Render.LEFT + _Render.DEL_CH) * len(v))
            self._write(b''.join(self.render_line[diff:]))

        self.last_current_line = list(self.current_line)
        self.last_cursor_ptr   = self.cursor_ptr

    def _bell(self):
        self._write(BELL)

    def _write(self, data: bytes):
        if not data:
            return
        data = data.replace(IAC, IAC + IAC).replace(b'\n', b'\r\n')
        self._write_raw(data)

    def _write_raw(self, data: bytes):
        self.conn.send_bytes(data)

    def _send_cmd(self, cmd: bytes, opt: bytes = None):
        if cmd in (DO, DONT):
            if (cmd == DO and self.DOOPTS.get(opt) is not True) or \
               (cmd == DONT and self.DOOPTS.get(opt) is not False):
                self.DOOPTS[opt] = (cmd == DO)
                self._write_raw(IAC + cmd + opt)
        elif cmd in (WILL, WONT):
            if (cmd == WILL and self.WILLOPTS.get(opt) is not True) or \
               (cmd == WONT and self.WILLOPTS.get(opt) is not False):
                self.WILLOPTS[opt] = (cmd == WILL)
                self._write_raw(IAC + cmd + opt)
        else:
            self._write_raw(IAC + cmd)


class MoyuConsole(InteractiveConsole):
    def __init__(self, conn: 'TelnetConnection', local_vars: dict):
        super().__init__(locals=local_vars)
        self.conn = conn
        self._buf: StringIO | None = None

    def set_buf(self, buf: StringIO):
        self._buf = buf

    def write(self, data: str):
        if self._buf is not None:
            self._buf.write(data)
        else:
            data = data.replace('\r\n', '\n').replace('\n', '\r\n')
            self.conn.send_str(data)

    def showtraceback(self):
        sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
        import traceback
        lines = traceback.format_exception(sys.last_type, sys.last_value, sys.last_traceback)
        self.write(''.join(lines[1:]))

    def showsyntaxerror(self, filename=None):
        sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
        import traceback
        lines = traceback.format_exception(sys.last_type, sys.last_value, sys.last_traceback)
        self.write(''.join(lines))


class TelnetConnection:
    def __init__(self, writer, local_vars: dict, banner: str = ''):
        self._writer = writer
        self.console = MoyuConsole(self, local_vars)
        self.handler = TelnetHandler(self)
        self._ps = '>>> '
        self._more = False

        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '

        if banner:
            self.send_str(banner + '\r\n')
        self.send_ps()

    def raw_input(self, data: bytes):
        self.handler.handle_input(data)

    def receive_line(self, line: bytes):
        try:
            text = line.decode('utf-8', errors='replace').rstrip('\r\n')
        except Exception:
            return
        if text in QUIT_FLAGS:
            self.close()
            return
        buf = StringIO()
        old_out = sys.stdout
        sys.stdout = buf
        self.console.set_buf(buf)
        try:
            more = self.console.push(text)
        except SystemExit:
            sys.stdout = old_out
            self.console.set_buf(None)
            self.close()
            return
        finally:
            sys.stdout = old_out
            self.console.set_buf(None)
        output = buf.getvalue()
        if output:
            output = output.replace('\r\n', '\n').replace('\n', '\r\n')
            output = output.rstrip('\r\n')
            self.send_str(output + '\r\n')
        self._more = more
        self._ps = sys.ps2 if more else sys.ps1
        self.send_str(self._ps)

    def send_ps(self):
        self.send_str(self._ps)

    def send_str(self, s: str):
        self.send_bytes(s.encode('utf-8', errors='replace'))

    def send_bytes(self, data: bytes):
        try:
            self._writer.write(data)
        except Exception:
            pass

    def close(self):
        try:
            self._writer.close()
        except Exception:
            pass


class AsyncTelnetServer:
    def __init__(self, host: str, port: int, local_vars: dict,
                 banner: str = 'MOYU REPL\nAvailable: controller, recipe, cube, scrcpy, detector, logger'):
        self._host      = host
        self._port      = port
        self._locals    = local_vars
        self._banner    = banner
        self._pre_cmds: list[str] = []

    def add_pre_cmd(self, cmd: str):
        self._pre_cmds.append(cmd)

    async def start(self):
        import asyncio
        server = await asyncio.start_server(self._handle, self._host, self._port)
        addr = server.sockets[0].getsockname()
        print(f'[Telnet] listening on {addr}')
        async with server:
            await server.serve_forever()

    async def _handle(self, reader, writer):
        import asyncio
        loop = asyncio.get_event_loop()
        addr = writer.get_extra_info('peername')
        print(f'[Telnet] connected: {addr}')
        conn = TelnetConnection(writer, dict(self._locals), banner=self._banner)
        for cmd in self._pre_cmds:
            conn.receive_line(cmd.encode())

        async def _drain():
            try:
                await writer.drain()
            except Exception:
                pass

        while True:
            try:
                data = await reader.read(1024)
            except Exception:
                break
            if not data:
                break
            if data.strip():
                logger.info("[Telnet] data(len=%d): %r", len(data), data[:64])
            conn.raw_input(data)
            await _drain()
        print(f'[Telnet] disconnected: {addr}')
