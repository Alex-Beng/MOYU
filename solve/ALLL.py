# ALL 1LLL algs to enhance perf
# FYI: https://drive.google.com/drive/folders/1HcO-MxEb0U6nVGBpqWhsBoRO6eZdw6bo

EX_ALLLS = {}

def update_all(perfix, algs_str):
    global EX_ALLLS
    algs = algs_str.splitlines()[1:]
    EX_ALLLS.update({f"{perfix}_{i+1}": algs[i] for i in range(len(algs)) })

AU = """
"U2 R' U2' (R2 U R' U') R' U2' (r U R U' r')
U2 (R' F R U' M' U2 M) (U' S R' F' R S')"
"U' (L F' L' S') (L F L' S)
U (S' R U' R') (S R U R')
U2 (r U R' U' M) (U R U' R')"
"U2 (R' F R S) (R' F' R S')
U' (l' U' L U M) (U' L' U L)"
"U2 M U M' U2 M U M'
M' U M U2 M' U M"
U' M U' M' U2 M U' M'
U' (M' U M U)2 M' U M
"(L' U2 L2 U F' L') (D' L2' D F L U' L')
U2 (L' U' L U' L' U2 L) U' (r U r' U R U' R' r U' r')"
"U (R U2' R2' U' F R) (D R2 D' F' R' U R)
U' (R U R' U R U2' R') U (l' U' l U' L' U L l' U l)"
U (R' U' F' U F R) U' (f R U R' U' f')
(F R U R' U' F') (R' U' R' F R F' U R)
U2 M' U' M2' U' M U2 M' U' M'
U' M' U M2' U M U2 M' U M'
"""

AD = """
"(R' U' R U' R' U2' R) U (R' U2' R U R' U F' U' F U R)
U' F (R U2' R' U) F' R U' r' F2 U F' U' M'
U L2' D' (l U' l' D) L2 U F U F'
R2 D (r' U r D') R2' U' F' U' F
U' (F U' F' U) (L' U L U) (L' U' L U2') F U2' F'
U' r2 D (r' U r D') r2' B (r U' r' B')
↑r2' D' (r U' r' D) r2 F' (r' U r F)
U2 (F' U F U') (R U' R' U') (R U R' U2) F' U2 F
U' (R U2' R' U2 R' F R F') (R U' L' U R' U' L)
U (R U R' U) (R' F R F') (R' U2' R2 U R2' U R2 U' R')
U F (R U' R' F) (R' F' R U2) (R' U' F' U F R) F'
(R' F R U R' U' F' U R2) (U R' U' R' F R F')
"""

AB = """
U M(R U R' F' R U R' U' R' F R2 U' R' U') M'
U' (L U F U' F'·L) (D L' U2' L D' L' U2' L')
"U' (l' U' L U M) (U' F L' U' L U L F' L2' U L)
 (F R U R' U') (R' F' U' F R F' U' R' U2' R)"
U' (F' L F U' L') U2' (L' U2 L U') L U2 L'
"U' (F' L F L' U2' L' U2 L) U (L' U2 L U L' U L)
U2 R' F U F (R U2 R' U') F' U'↓R' F2 R2"
"U2 (R u R' U R U' R u' R2') U' (R f R' f')
U' F' (L' U' L2 U L') (U' L' U L F) (U L U' L')
U r' U F2 U F (R' F R U) F' U2 F r"
U2 (r U R2' F' R) (U R U' R') (F R U' r')
U' (L U L' U') (L U L' U2') (L F' L F L2') (U' L U' L')
U' (l' U' L U) (l F' L2' U L U) (L' U' L F)
U' (L' U L U2') (L U F' L' F) (L U' L2' U L)
U' (F' L F L') U2' (L' U L U') (L U L2' U L2 U2 L')
U' (L F' L' F) (L F' L2' U' L U) (L F L2' U' L)
"""

AF = """
U F' R' F R2 U R2' F R F U F2
U (↑ L U' L' U2) (L2 U F U' F') L' U' L'
U2 F U (R' F R F') (R' U2' R2 U) R2 U R F'
U' (r U R' F') (R U R' U') (R' F R2 U' r')
(F' L' U' L) (F' L F L2' U2 L U) (L' U' L F)
U' (R U R' U R U2' R') U (R U2' R' U2 R' F R F')
"U2 (R f R' f') U (R2' u' R U' R U R' u R)
U2 (R' U' R U) F (R U R' U') (R' U R2 U' R' F')"
(MR U R' U) (R U2' R' U) (R' F R F' r U R')
(R U2 R' U) R' U' F U R U' F' R U2 R'
U (↑ L U L' U) (L2 F' L' F L') U2 (L U' L' U L U' L')
U2 (L' U2 L U2' L F' L' F) (L' U' L U' L' U2 L)
(R' U2' R U') (R' F' U F) U' R2 U2' (R' U' R U') R'
"""

AL = """
"M(L' U' L F L' U' L U L F' L2' U L U) M'
U2 x R2' U2' (R U R' U2) L U' R U M"
U2 (R' U' F' U F·R') (D' R U2 R' D R U2 R)
U2 (r U R' U' M) (U F' R U R' U' R' F R2 U' R')
U2 (F R' F' R U2 R U2' R') U' (R U2' R' U' R U' R')
U2 (F R' F' U R) U2 (R U2' R' U) R' U2' R
"U' (L' u' L U' L' U L' u L2) U (L' f' L f)
U2 F (R U R2' U' R) (U R U' R' F') (U' R' U R)"
U' (l' U' L2 F L') (U' L' U L) (F' L' U l)
U2 (r U R' U') (r' F R2 U' R' U') (R U R' F')
U2 (R' U' R U) (R' U' R U2) (R' F R' F' R2) (U R' U R)
U2 (R U' R' U2) (R' U' F R F') (R' U R2 U' R')
U2 (F R' F' R) U2 (R U' R' U) (R' U' R2 U' R2' U2' R)
U2 (R' F R F') (R' F R2 U R' U') (R' F' R2 U R')
"""

AR = """
U2 x' U (R U' R2' F') (R2 U' R' U') F' U2 x
U2 (R U R' U') F2 (r U r' F2) U (R U' R2' F') R
(↑R' U R U2') (R2' U' F' U F) R U R
U2 (L' U' L U' L' U2 L) U' (L' U2 L U2' L F' L' F)
U (R' F' U' F) R U F (R U R' U') (R' U R U') F'
U2 R2' F R U F' (R U R' U) F U F' U R
U2 (l' U' L F) (L' U' L U) (L F' L2' U l)
U (F R U R') (F R' F' R2 U2' R' U') (R U R' F')
"U' (L' f' L f) U' (L2 u L' U L' U' L u' L')
U' (L U L' U') F' (L' U' L U) (L U' L2' U L F)"
(↑R' U' R U') (R2' F R F' R) U2' (R' U R U' R' U R)
U' (R U R' U R U2' R2') (F R F' U2 F' U2 F)
U' (R U2' R' U2 R' F R F') (R U R' U R U2' R')
"""

update_all("AU", AU)
update_all("AD", AD)
update_all("AB", AB)
update_all("AF", AF)
update_all("AL", AL)
update_all("AR", AR)

BU = """
"U' (S R' F' R S') (R' F R U' M' U2 M)
(M' U2 M U) (R' F' R S R' F R S')"
U' (R U R' S') (R U' R' S)
U (R U' R' S') (R U R' S)
"(↑R2' S2 R F) U' (R' S2 R U) F' R
(r U M U R' U' r U' r') (R U R' U R U2' R')"
U' (R' U' R F D R2 D') (R' F' U R2 U2' R')
U (L U L' F' D' L2' D) (L F U' L2' U2 L)
(M' U' M U) (M' U' M U') M' U2 M
(M' U M U') (M' U M U) M' U2 M
"""

BD = """
U2 (r' U r U') r' F' U' (r U2 R' U' R U' r') F r
U2 (F' U2 F U2') (R U' R' U) (R U R' U) F' U' F
U (↓B r U r' B') (r2 D r' U' r D' r2')
U' (↑F' r' U' r F) (r2' D' r U r' D r2)
U F (R' F R F') U' (F U r U2 r' U' R U R' F2)
(R U' R' U') (F U R U' R' F) (r U2' R' U') r' F R
U R' F' U2 F U' (R U R2' F R F') U2 R
(R U' R2' F R F') (R U' B U2' B' R')
"""

BB = """
U2 (F R' F' R2 U' R') (F' U' F) R U R'
↑R' U' R' (F' U' F U) (R2 U2' R' U' R)
↑ L U L (F U F' U') (L2' U2 L U L')
(R' U R U') R' F U (R' F R F') U' R' F' R2
M' U (r' F R F') U (R U R' U2) r U r'
U2 F (R U' R' U) (R U2' R2' F R F') (R U' R' F')
"U2 F' (L' U L U') (L' U2 L2 F' L' F) (L' U L F)
 U F U' (R U R' U2') R U (R2' F R F') U2 F'"
(L U2 L' U) (L' U2 L U2') (L U F' L' F)
(R' U2' R U') (R U2' R' U2) (R' U' F R F')
U2 F (R U' R' U2') (R U R' U) (R' U2' R2 U) R2 U R F'
U (R U' R2' F R) U (R U' R2' F' R) (F R' F' R)
"U' (L' U L2 F' L') U' (L' U L2 F L') (F' L F L')
 (F U R U2 R' U' R U R' F') U' (R' U' R U' R' U2' R)"
"""

BL = """
U (↑R' U2 R' D' R U2 R' D R) (F' U' F U R)
U (↑ L U2' L D L' U2' L D' L') (F U F' U' L')
U2 R' F' U2 (R' F R U') (R' F' R U') F U' R
U2 (R' U2' R U') R' U' (R' F R F') (R U2' R' U2 R)
U2 (R U2' R' F) U R' U' F' U (R U' R U2' R')
U2 (R' U' R U') F U' (R' U' R U) (R U' R' U') (R U R' F')
U2 (R2 U R' U) (R' U' R U') R' F U R U' F' R'
U' (R U R' U') F' U' (R' U' F' U F R) F U2 (R U' R')
U2 F (R U' R' U) (R U R2' F') (r U R U' r')
F' (L' U L U') (L' U' L2 F) (l' U' L' U l)
U2 (L' U2 L U L' U L) (F' L F L' U2' L' U2 L)
(R U2' R' U' R U' R') (F R' F' R U2 R U2' R')
"""

update_all("BU", BU)
update_all("BD", BD)
update_all("BB", BB)
update_all("BL", BL)

C1U = """
U2 F (R U R' U')2 F' (r U R' U R U2' r')
U' (r' U' R U2') R' U2 F' (r U' r' F2) U r
U2 (F R U R' U') (R U R2' F R F' R U' R' F')
(R U' L' U R' U' L) U (L' U' L U L F' L' F)
(L' U R U' L U R') U' (R U R' U' R' F R F')
(F R U R' U') (R U R' F2) r U r2' F r)
U' (R U' R' F) (R U R' U')2 F' U R U' R'
(F R U R' U') (R U R' F R' F' R2 U' R' F')
R U2 (R U R' U') (R' U2' F R F') U (R2' F R F')
U' (R U R' U2') F2' U' (r' F r2 U r' F)
U' (r U r' U) (R U' R' U2') (R U' R' U2) r U' r'
U' (r' U' r U') (R' U R U2)2 r' U r
"""

C1D = """
(R U R' U R U' R' U R U2' R2') (U' F' U F R)
(L' U' L U' L' U L U' L' U2 L2) (U F U' F' L')
U r' D' (r U' r' D) (R2 U' R' U) r U R'
U2 R2' D' R (F R U R' U' F') U R' D R2
R U R2' F' R U2 (F' U F U) (R' F R2 U' R')
F' U2 F U (R2 U R' U) (R U2' R2' U') F' U2 F
"U↑ L U (L F' L' F) (L' U L U') (L' U L U2' L')
U'↑r2' F2 R (F' U' F U) R' F2 r2"
U'↑R' U' (R' F R F') (R U' R' U) (R U' R' U2 R)
U2 (R U' R' U2) F' U F (R U R' U) R U R'
F R F' (r U R' U2) (r' U' r U) (r' F' U F)
(R' F R U) (r U2' r' U) (r U2' r' U') F' R U2' R'
"↓F (R U R D) (r' U' r D') R2' U' F' (U' L' U L)
(↑R' F R B') (R' D' R' D) F' (D' R U'D R U) B
U2 (↓R2 U R' U') (R' F R U R' U) (R F' R') (U' F U' F')
U' (R' U' R' F R F' U R) U' (R U2' R' U' R U R' U' R U' R')"
"""

C1B = """
U' (F' U' F U') (R U' R' U') (F R' F' R)
U (F U F' U) (L' U L U) (F' L F L')
(R U R' S) (R' F R f') (U R U R')
U2 (R U R' U' R' F R F') (R' U' R U' R' U2' R)
U2 (L' U' L U L F' L' F) (L U L' U L U2 L')
U' (R U' R' F) R' F' (R2 U' R' U2') (R U' R' U') R U R'
U' (R' U R U) (R2' F R F' R) U2' (R' U R U) R' U' R
"U2 (F' L' U' L U F) (L' U2' L' D' L U2 L' D L2')
U (R' F' U' F U R) U' (R' U2 R' D' R U2 R' D R2)"
U2 (F R U R' U' F') (R U2 R D R' U2' R D' R2)
(R U2' R' U') (R U R' U) (F' U F) (R U' R2' F R F')
"R' U2' (R U R' U) (F R U R' U' F2) U F R
U' (l U L' U L U2 l') U (L' U' L U L F' L' F)"
U (r' U' R U' R' U2' r) U' (R U R' U' R' F R F')
"""

C1F = """
U2↓F R F' (r U r' U) (R' U' r U' r')
U2↓ F' L' F (l' U' l U') (L U l' U l)
(R U R' U' R' F R F') (R' U2' R U R' U R)
↓F U2' F2·U' (L' U L2 F L2' U L)
↓ F' U2 F2'·U (R U' R2' F' R2 U' R')
"(L' U2 L2 F' L' F) (L' U L U) (L F' L' F)
U2 (f U R U' R' f') U' (F R' F' r U R U' r')"
(R U2' R2' F R F') (R U' R' U') (R' F R F')
(R' U2' R2 U R2' U R U2') (R' F R F')
"(L U2 L2' U' L2 U' L' U2) (L F' L' F)
U (R U R' U) (R' U2' R2 U) R2 U R F' U F R U' R'
U2 (r U2 r' U' R U' R') (F U F' U') R' F' R
U (R U R' U) (r U2' r' U) (F' U' F U) r U r'
"""

C1L = """
U2 (R U2' R') (F R U R' U' F') (U R U R')
U2 F' U2' L D (L' U2' L D') (L2' U' L U) F
(L' U' L U' L' U2 L) (F R' F' R U R U' R')
(R' F' U' F) U' (F R U R' U' F2) U2 F R
U (f' L' f U) (l U L' U' M')
U2 (F R U R' U') (R' F' r U R U' r')
U' L U L' (F' L F U' L') (U2' L' U2 L)
U2 (R U2' R' U) (R' F' U' F U R2) U R'
"U' M' U' L U· l D (l' U' l D') L2'
 U (F U R U' R' F') (R U2' R' U' F' U F R U' R')"
(↓F R U R' U') (R F' r U R2·U' r' F R F')
U2 (L U2 L' F') (L' U' L2 U L' F) (U L U L')
U' (F' L F U F' L' F) (L U L' U') (L U L' U') (L U' L')
"""

C1R = """
U2 (L' U2 L) (F' L' U' L U F) (U' L' U' L)
U2 F U2 R' D' (R U2 R' D) (R2 U R' U') F'
(R U R' U R U2' R') (F' L F L' U' L' U L)
U' F (R U R' U) (R' F' U' F U R2) U2' R' F'
U' (f R f' U') (r' U' R U M')
U2 (F' L' U' L U) (r U R' U' r' F R)
U R' U' R (F R' F' U R) (U2 R U2' R')
"U2 (L' U2 L U') (L F U F' U' L2') U' L
 R' U2' R (F R U R' U' F') (U' R' U' R)"
U M' U R' U'·r' D' (r U r' D) R2
(↓ F' L' U' L U) (L' F l' U' L2'· U l F' L' F)
"U2 (R' U2' R F) (R U R2' U' R F') (U' R' U' R)
(R U' R' U) F U2' (r U2' r' U2) (R' F' R)"
U (F R' F' U' F R F') (R' U' R U) (R' U' R U) (R' U R)
"""

update_all("C1U", C1U)
update_all("C1D", C1D)
update_all("C1B", C1B)
update_all("C1F", C1F)
update_all("C1L", C1L)
update_all("C1R", C1R)


C3U = """
U2 (R U2' R2' F R F' R U2' R') (F' L' U' L U F)
"U2 (L' U2 L2 F' L' F L' U2 L) (F R U R' U' F')
U (R U2' R2' F R F' R U2' R') U' (F R U R' U' F')"
U (L' U' L U') (L F' L' F)2 (L' U2 L)
U' (R U R' U) (R' F R F')2 (R U2' R')
(r U2' R' U' R U' r') F (U R U' R')2 F'
U' (R2 D r' U2 r D' R2') U2' (R' F R F')
U (L2' D' l U2' l' D L2) U2 (L F' L' F)
U (R U2' R') (F R' F' R) (F' U F) (U2 R U' R')
U' (L' U2 L) (F' L F L') (F U' F') (U2' L' U L)
U (R U2' R2' F R F' R) U2' (R2' F' U' F U R)
U (R U R' U2') F' (r U' r' F2) (U2' R U' R')
U2 (F R U R2' F R F' R U' R') (U R U' R' F')
"""

C3D = """
U↑R' U' (R' F R F') U R
U'↑ L U (L F' L' F) U' L'
(R U R' U R U2' R') (F' U' L' U L F)
U' (R' U2' R U R' U R) (L U F U' F' L')
"U2 (L2' U S U2 S' U L') (U F U' F' L')
(l' U' L U' L' U2 l) (f U R U' R' f')"
"U2 (R2 U' S' U2' S U' R) (U' F' U F R)
(r U R' U R U2' r') (f' U' L' U L f)"
U2 S (R' U' F' U F R) U S'
U2 S' U' (F U R U' R' F')S
"U2 (f' U' L' U L f) (L' U2 L U L' U L)
U' (R' F' U' F U R) U (R' U2' R U R' U R)"
U2 (f U R U' R' f') (R U2' R' U' R U' R')
U' (R U2' R' U) (F' U2 F) (R U' R') (F' U2 F)
(R U R' U R U2' R') U (R U R' F' U2 F R U' R')
"""

C3B = """
U' R' D (R' U' R UD') R U' F (R2 U R' U') F'
U R2' D' (r U r' D) (R2 f R' f')
U R2 D (r' U' r D') (R2' F' U F)
U2 R' F U R U R2' F' (R2 U' R' U') R U' F U F'
U' (R' U' F U R U' R' F' R) (F R' F' R U R U' R')
"U (L U F' U' L' U L F L') (F' L F L' U' L' U L)
(F R U R' U' F') U' (L' U R U' L U R')
(F' L' U' L U F) U (R U' L' U R' U' L)
(F U R U' R') (U F' R' F R U' R' F' R)
(F' U' L' U L) (U' F L F' L' U L F L')
U' (F' U' F U) (R U R' U2) (R U2' R' U2) F' U' F
U (F U F' U') (L' U' L U2') (L' U2 L U2') F U F'
"""

C3F = """
F (R U R2' U' R) F' (U' R' U2' R)
U R' F' U' (R U R' U') R' F (R2 U' R' U) R
U2 (R U R' F') (R U R' U') (R' U' F) (U R2 U2' R')
"U2 (L' U' L F) (L' U' L U) (L U F') (U' L2' U2 L)
↑R' F (R U' R' U2') (R U R2' F' R) U R"
U (R U2' B U' B' R') U (R U R' U') (R U2' R')
"U' (L' U2 B' U B L) U' (L' U' L U) (L' U2 L)
U R' U2 F' U F (R U' R' U') (R U R' U2') R"
U R' U' R (F U R U' R' F') U' (R' U' R U R' U R)
U (R U R' U) (R' U' F' U F R2) U (R' U' R U') R'
"U' (L' u' L U') (L' U L' u) (L f' L f)
U (R' u' R U') R' U R' u R F' U F"
U (R u R' U) (R U' R u') (R' f R' f')
U (R' U' R U' R' U2' R) (F R' F' R U R U' R')
U2 (r U r' F) (R U R' U') F2 U F U' r U' r'
"""

C3L = """
U F (R U' R' F) (R' F' R U2) (R U' R' F')
U2 (R U2' R' U') (R' F' U' F) (U R2 U2' R')
(R' F R U) (R U2' R2' F') (R2 U2' R' U) F U2 F'
F U (R U2' R' U' R U' R') F' (R' F R U2) R' F' R
(R U' R' U') F' U F (R' F R F' R U R')
U (F R U' R') (f U R U' R' f') U' (R U R' F')
F U2 R' F2 (R U2 R U2') R' F2 (R U' R' U') F'
U R' U' F' U F' (r U2 R U') r' F
U F (R U' R' F) U (R U' R' F') U' (R U R' F')
"U2 (F' L F L' U' L' U L) (F R U' R' U2 R U R' F')
F' U (R U R' U) M F (r U2' R' U) F"
U2 (R' F R U) (R' F' R U) F U2 F'
F R2 U2' R2' (F R' F' R2 U' R) U' R2' F'
"""

C3R = """
U2 (F R' F' R U R U' R2') (U' F' U F R)
U (R' F' U' F) (R U R' F) (R U R' U') R' F' R2
"U' (F' L' U L) (f' U' L' U L f) U (L' U' L F)
U (R U2' R2' F2) U' (R2 U' R2' U) F U F R"
↑r' U' M' U2 (r' F R F') (r U2' r' U r)
U2 (R U' R' U') M' F' U2 F U R U' r'
U2 (L' U2 L U) (L F U F') (U' L2' U2 L)
U r R D (r' U r D') r' (R' U R U2 R')
U R2' U (R2 U R' U') F' U F R' U' R2
"U2 (F R' F' R U R U' R') (F' L' U L U2' L' U' L F)
U2 (R' U R U') R2' U' F' U F (R U R U) R' U' R"
U (R U R' U) (R U' R') (F' U F) (R U' R')
U2 (L F' L' U') (L F L' U') F' U2' F
F (R U' R2' F R F') U' (F R' F' R2 U R' U') F'
"""

update_all("C3U", C3U)
update_all("C3D", C3D)
update_all("C3B", C3B)
update_all("C3F", C3F)
update_all("C3L", C3L)
update_all("C3R", C3R)

DHU = """
U2 (MR U R' U) (R U' R' U) (r U2' r' U') M'
"U (F U R U' R' F') (R U R' U R U' B U' B' R')
R U2' R2' (F R U R' U' F') U R U (R' F R F')"
"U' (F' U' L' U L F) (L' U' L U' L' U B' U B L)
U2 (R' U' F' U F R) U (R' F' U' F U' R U R' U R)"
U2 (r U R' U R U2' r') U (l' U2 L U L' U l)
(l' U' L U' L' U2 l) U' (r U2' R' U' R U' r')
"U2 (L F U F' U L' U' L U' L') (F' L' U' L U F)
U2 (R' F' U' F U' R U R' U R) U (R' F' U' F U R)"
U2 (R' F' U' F U' R U R' U R) (F R U R' U' F')
U2 F R U' R2' F2 (r U r' F) (R2 U R' U) (R U' R' F')
"""

DHD = """
U (R' U R U2) (R' U' R U) R' U' (R' F R F2) U2 F R
F U' (R U R' U') F' U' F (R U R' U') (R U' R' F')
U F (R U R' U) (R U' R' F') U F U (R U' R' U) F'
U' (f' U' L' U L f) (L F' L2' B L2 F L2' B' L)
U' (f U R U' R' f') (R' F R2 B' R2' F' R2 B R')
U2 (L' U2 L2 F' L' F L' U2 L2) (F l' U l F2' L')
U2 (R U2' R2' F R F' R U2' R2') (F' r U' r' F2 R)
U (R' U' F R' F' R U R) F' (U' L' U L)2 F
"""

DHB = """
(R U2' R2' F R F') U2' (R' F R F')
(R U2 R' U') (F' U F U) (R' F R F) (r U r' F)
U' F (R U' R' U2) (R U R' U) (R' U' F' U F R) F'
U' F U (R' F R F') U2 (R' F R F') (R U R' F')
U F' U' (L F' L' F) U2' (L F' L' F) (L' U' L F)
(F R U R' U' F') (R U2 R' U' F' U F R U' R')
(R' F' U' F U R) U' (R' U' F U R U' R' F' R)
"U' (F R' F' R U2 R U2' R') (f' L' U' L U f)
(F U R U' R') (U F' U' R' F' r U M)"
U (F' L F L' U2' L' U2 L) (f R U R' U' f')
"(↑ L U L F' L' F U') (F' L' U' L U F2' U' F' L')
F U (R U2 R' U') (R U B' R B R2') F'"
(↑R' U' R' F R F' U) (F R U R' U' F2 U F R)
U R' F' (r U2 r' F2) (R U' R' U') (R' F R U R)
"""

DHL = """
U2 (R U' R2' D') (r U' r' D) R2 U R'
U' (R' U R2 D) (r' U r D') R2 U' R
U' R' F' U' F R' F (R2 U' R' U2) (R U R' F') R
U2 (R' F R F) U2' (R' F' R U2')↓F2 R U2 R'
(L F' L' F') U2 (L F L' U2) F2' L' U2' L
U2 (R U2' R2' F R) F2 U2 F (R U' R' U) R U' R'
U' (R2' F R F') U2 (R' U' F' U F R2) U' R' U R
"U (R U R' U) (R U' R' U) (R' F R F') U2 (R' F R F')
U (R' U' R U' R' U F' U F) (R2 U R' U' R' F R F')"
"U (L' U' L U') (L' U L U') (L F' L' F) U2' (L F' L' F)
U (L U L' U L U' F U' F') (L2' U' L U L F' L' F)"
U (R U R' U2) F2 (r U r' F) U (R' F R F')
U2 (F' L F L') U2' (L' U L U') (L F' L' F) L' U2 L
(F R' F' R) U2 (R U' R' U) (R' F R F') (R U2' R')
"""

update_all("DHU", DHU)
update_all("DHD", DHD)
update_all("DHB", DHB)
update_all("DHL", DHL)


DLU = """
U2 r' U' (r U2' r' U) (R U2' R2' U') (R U' R' U2') R U' r
U2 (l U2 L' U' L U') (M' F R' F R F2' L')
U (R' F R F' R U2 R' U' F' U') (F2 R U R' U' F')
U' F U' (R U R' U2) (F' U F U) (R U2 R' U) F'
U2 F' (r U' r' F2) U' (R U R' U2) M' U R U' r'
R' U F' U2 F U (R U R' U2) (F' U F U') R
U' (F R' F' R2 U R' U') (F' U' F) (R U R' U') (R U2' R')
U2 (F' L F L2' U' L U) (F U F') (L' U' L U) (L' U2 L)
U' (r' U' R U' R' U2' r) (l' U2 L U L' U l)
U2 (R U R' U) (R' F R U R' U' F' U R) U (R' F R F')
U' (L' U2 L U') (L' U L) (F U' F' U') (L' U L2 F' L' F)
U2 (R U2' R' U) (R U' R') (F' U F U) (R U' R2' F R F')
"""

DLD = """
"U' F (R U' R2' U') (F' U F U2') (R2 U R2' U) R U' F'
U' (R U2' R2' F R F' R U2' R') U f (U R U' R')2 f'"
U2 (R' U2 R' D') (r U' r' D) R F' U2 F U R
U2 r' F U' (R U' R' U2) r F U (R U' R' U') F'
(R U B U' B') (M' U M U R' U' r U' r')
U' M' U (MR U2' R2' F R F') r U2 r'
U' r U2 r' (F R' F' R2 U2' R') M' U' M
"U' (L' U' L U) (L F' L' U) (L F' L' F) (L' U2 L U) F
U2 (r' U' r U' R' U M U r) U (f U R U' R' f')"
"U2 (R U R' U') (R' F R U') (R' F R F') (R U2' R' U') F'
U (r U r' U R U' M' U' r2'x) B' U' B U L"
U2 (R U' R' U) (R U' R' U') F' U2 r' F r2 U' r' F2
(r U' r' F2) (R U' R' U) (R U' R' U') F' U2 r' F r
U2 (R U' R2' U') F' U F2 R F' U2 (R U R' U) R U R'
U' (r U2' R2' F R F' R) U' (R' U2 R U2') (r' U2 r U' r')
"""

DLB = """
U2 (R U R' U) (R' F R F') U2' (R' F R F')
U (R U R D) (r' U M' U) R D' (R2' U R U R')
U2 L F (R' U' R2 U' R2' U2' R U' R U2' R') F' L'
"(F' L F L2' U' L) (F U2' F') (L' U L U') (L' U2 L)
U' (R2' F R F') U2 (R U2 R' U') (R U R' F') U2 F R"
U2 (l U2 L' U' L U' l') (L' U2 L U2' L F' L' F)
(R' U' F' U F R) U2 (R U R' U' R' F R F')
"(L U2 L' U' L U2 L2') (D' l U' l' D L2 U L')
U2 (R U2' R' U' R U2' R2') (D' r U' r' D R2 U R')"
U (R U2' R' U) F' U' F2 (R U R' U') F' U R U R'
U' F U (R U' R' U') (R U' R' F') U' F (R U2 R' F')
R' U' (R' F R F') (R U' R') (f U R U' R' f') U' R
U' (F R' F' R) U2 (R U' B U' B' R')
U2 (R U2 R' U) F2 (r U r' F) U (R' F R F')
"""

DLF = """
"(R' U' F U R U' R' F' R) (L F U F' U' L')
(R' U' F U R U' R' F' R) U' (F R U R' U' F')"
U F (R U2' R2' U') F' U F R U2 F'
U (F' L F L') (U' S L' U L S')
U2 (r' U' R' F2) R F' U r F U2 F'
F (R U' R' F) U (R U' R' F') U (R U R' F')
(R' U' F' U F R) (L' U' L U L F' L' F)
U' (F' L F L') U2 (F' L F U L2' U L2 U2 L')
U (M' U M U2) (R' F R U) F U' F'
U2 (F U R U' R' F') (R' U2' R U R' F U R U' R' F' R)
U2 (R' F R U') M' U2 r' U' F' U R
U' L F D' (L2' U2 L2 D) F2' (L' U L F L')
(R' U R2 D) (r' U r D') R2 U2' (R U' R' U2') R
"""

DLL = """
U' (L' U' L U') (L F' L' F) U2 (L F' L' F)
U F U' (R U' R' F') U' F (R U R' U) (R U R' F')
U2 (R U R' U') (R U R' F') (L' U' L U') F U' R U' R'
U (F R' F' R2 U R') (F' U2 F) (R U' R' U) (R U2' R')
U (R' U2' R U R' U2' R2) (D r' U r D' R2' U' R)
U' (R' U' R' F') U' F U R2 U2' R' U2 F' U F R
U' (r' U2' R U R' U r) (R U2' R' U2 R' F R F')
"U (L U F U' F' L') U2' (L' U' L U L F' L' F)
(F U R U' R' F') U (F R U' R' U R U R' F')"
U' (R' U R2 D) (r' U r D') R2 U (R U R' U) R
U (F R U' R' U R U2 R' U' F') U' (F R U R' U' F')
U R' U F' U' F (R U R' U) F' U F R
U F U (R U' R2' F') U' F R F' (R' U' R U) R' U R
"""

DLR = """
U (L U F' U' L' U L F L') (R' F' U' F U R)
U' R' F' U2 F2 U (R U' R' F') U2 R
(F R' F' R) (U S' R U' R' S)
(F R' F' R2 U' R') U' F (R U R2' U') F' U R
M' U' M U2 (r U' r' U') F' U F
U' (R U R' F') U (R' U' F' U F R) U2 F R U' R'
"U2 (F R' F' R) U2' (F R' F' U' R2 U' R2' U2' R)
U2 (F R' F' R U R U' R') U2 (R' U' R' F R F' U R)"
"U (L U F U' F' L') (R U R' U' R' F R F')
U2 F (R U R' U2') (R U' R' F) (R U R' U') F' U2 F'
U' (r U' r' U) M' U2 R B U B' r'
U2 R' F' D (R2 U2' R2' D') F2 (R U' R' F' R)
U' F' U2 F U2 (r U r' U2) M' U M
"""

update_all("DLU", DLU)
update_all("DLD", DLD)
update_all("DLB", DLB)
update_all("DLF", DLF)
update_all("DLL", DLL)
update_all("DLR", DLR)


DPiU = """
U' r U (M U R' U R U2' R') (U' R U' M') U' r'
"U F' (L' U' L U2') (L F' L' F) U' (L' U' L F)
U' (R' U2' R U R' F' U F R) (F R U R' U' F')"
U' F (R U R' U2) (R' F R F') U (R U R' F')
(r U r' U2') (R U R' U') R U' M' U' r'
U' r U (M U R' U) (R U' R' U2) r U' r'
"U' (f' U' L' U L) (S U' L' U L F)
U2↑r' U' r (U2' R' U2 R U2') r' U r"
U (f U R U' R') (S' U R U' R' F')
U' (F R U R' U') (R U2' R' U' M' U R U' r' U' F')
"U (F' L' U' L U) (L' U2 L U M' U' L' U l U F)
U2 (R U2' R' U2) (R' F R2 U R' U2') (R' F R F' R U R') F'"
"(L' U' L) (F U F') (L' U' L U2) (L F' L' F)
U2 F (R U' R' U2) (R U R' F') (R U B U' B' R')"
(R U R') (F' U' F) (R U R' U2') (R' F R F')
U (R' U' R' F R F' U R) U (R' U' F' U F R)
"""

DPiD = """
(r' U2' R U) R' F U r F U' F'
U2 F U F' r' U' F' (R U' R' U2) r
U' (R' U' F' U F R) (r U M U R' U' r U' r')
U (R U R' U) F' (L' U2 L F) U' R U' R'
U' r D' R2' U' (R U2 R' U) R2 D r'
U' r' D (R2 U R' U2') (R U' R2' D') r
U' (R' F' U' f) (U' R U R') S' U R
U' (R B U B' U') (M' U2' R' U' R U' r')
U2 (r U2' R' U' R U' r') (f R U R' U' f')
(f U R U' R' f') (r U R' U R U2' r')
U (r U R' U R U2') (M U B U' B' R')
U (r' U' R U' R' U2') (M' U' F' U F R)
"""

DPiB = """
(R' F R U') (R' U2' R U) R2' F' R F' U F R
U' (F R' F' R U R U' R2') (F' U' F U' R U R' U R)
U (F' L F L' U' L' U L2) (F U F' U L' U' L U' L')
U2 (R U' R2' D') (r U r' D) R2 U R'
(R' U R2 D) (r' U' r D') R2 U' R
U' (L' U2 L F2) U2 (L F' L' U2') (F L F L')
U (R U2' R' F2') U2' (R' F R U2) (F' R' F' R)
L' U2 L (F' L F L') U (L' U' L U2) (L F' L' F)
(R U2' R') (F R' F' R) U' (R U R' U2') (R' F R F')
(R U R' U') R U' (f U R U' R' f') (R2' F R F')
U R' F' U' (R U R' U') R' F R2 U' (R2' F R F') U R
U2 (R' F R F') U (R U R2' F R F') U F' U F
"""

DPiF = """
(R' F R U R' U' F' U R) U (R' U' F' U F R)
U2 (R U R' F' U' F U R U2' R') (F U R U' R' F')
"U2 (F R U' R') (F R' F' R) U2' (F R' F' R) U' F'
U L F' (L' U' L U) (F2' U F' U') (L' U2' L U L')"
U2 (F' L' U L) (F' L F L') U2 (F' L F L') U F
"U' (M' U' r' F R U F U') (R U R' U' F')
(f' U' L' U L f) (R U2' R' U2 R' F R F')"
"U (M' U l F' L' U' F' U) (L' U' L U F)
 U M' U (R U' r' U2) R' F R y' R' U R' U R"
(R' F R U) R' U' F2 U' (R U R' U R U2 R') F R
U' (r' U' M' U2) (r' F R F') U2 (R U R' U2) r
U' F (R U R2' U') F' U F (R U R' F R F') U' F'
R' (F' U' F U') (R U R' U) (F R U R' U' F') U R
U (F R' F' R) U2' (F R' F' R2 U2' R')
U (r' U' R U2) R' U2' F R F' (r U R' U) r' U r
"""

DPiL = """
U' (R U2' R' U2 R' F R) (S R U R' U' f')
U' F U (R' U' F' U F R) U (R U2' R' U') (R U R' F')
U2 (R U2 R' U') (F' U F U) (R' U' F' U F R2) U' R'
U' (R U2' R2' D') F' (R U' R' F) (r U r' D) R
"U' (R U R' U' R' F R F') (r' U r2 U' r2 U' r2 U r')
(F U F' U') (R' F' R) (U2 L F' L') (F R' F' R)"
U' (R U2' R' U2) (R' F R U') (R' F R F') U (R U R' F')
U2 (r U' r' F) U2 F U2 (R U' R' U') (R U R' F')
(f' U' L' U L S) (L F L' U2' L' U2 L)
U F U (R U' R2' F') U' F R F' U' R' U2' R
U' F (R U' R' U) (F R U R' U' F') (R U2 R' U') F'
"U2 (R' F R2 B' R2' F' R2 B R') (F' L F L' U' L' U L)
U (L F' L' F) (R' F' R U2) (L F' L') (U' F' U F)"
F (R U R' U2) (R' F R F') (R U2' R' U') F'
"""

DPiR = """
"U2 (L' U' L U L F' L' F) U2' (R U2' R' U2 R' F R F')
"U (L' U2 L U2' L F' L') (S' L' U' L U f)
U (R U R' F') U' (R U R' U') (R' F R U') (R' F R F')"
U F' U' (r U' r' F2) (R U2 M' U') (r' U r U r')
U (R U R' U) (R U' R2' F') U' F U (R U2 R' F) R F'
(f U R U' R' S') (R' F' R U2 R U2' R')
"U (L' U' L U L F' L' F) (R B' R2' F R2 B R2' F' R)
(F' U' F U) (r U r' U2) (R' F R F' r U r')"
(R' U2' R U) F (R' F' U F) (R2 U R' U') F'
U2 R' D' (r U' r' F') (R U R' F) D R2 U2' R'
U F U (R U2' R' U') (R U R' U) (R' F R F') U' F'
"U2 (r U' r2' U r2' U r2' U' r) (F R' F' R U R U' R')
U' (R' F R F') (L F L' U2') (R' F R) (U F U' F')"
U2 R' U' F' U F2 (R U R' F') R U F U2 F'
U F (U R U2' R') (F R' F' R U2) (R U' R' F')
"""

update_all("DPiU", DPiU)
update_all("DPiD", DPiD)
update_all("DPiB", DPiB)
update_all("DPiF", DPiF)
update_all("DPiL", DPiL)
update_all("DPiR", DPiR)


DS_U = """
U (F U R U' R' F') (R' F' U' F U R)
(R U B U' B' R') (F R U R' U' F')
U (r F R' U') R F' r' U2 F (R U' R' F')
U2 F' U2 F (R U' R2' D') (r U' r' D) R
U2 (R' U' F' U F R) U' (R' F' U' F U R)
(r' F' U' F U r) (F R U R' U' F')
(R U R' F' U2' F R U' R') (F U R U' R' F')
(R' F' U' F U R) U' (F R U' R' U2' R U R' F')
(r U R' U R U2' r') f' (U' L' U L)2 f
U' f (R U R' U')2 f' (l' U2 L U L' U l)
"(l' U' L U' L' U2 L) (U M U2' M' U M)
U (r' U2' R U R' U) (r2 U' r2' U r2 U r2' U' r)"
(Mr' F' r U') (R' F2 R U') M'
"""

DS_D = """
U' (l' U' L U' L' U2 l2) (U· L F' L' F U' l')
U' f (U R U' R')2 f' (R' F' U' F U R)
U' (R' U' R' F R F' U R2) (U R2' F R F2 U F)
U' (l' U' L U' L' U2 l) (f R U R' U' f')
(F U R U' R' F') U F (U R U' R')2 F'
U' L F U (R U R' U) (R U R' U') F' U2 r' x
U2 (R' F' U' F U R) U (R U R2' F R F2' U F)
U' (R' F r U) (r' F' R U2) F U (R U' R' U) F'
U F (R U R' U')2 F' (R B U B' U' R')
U (R' U' F' U F R) F (U R U' R')2 F'
U (L U F U' F' L') f' (L' U' L U)2 f
U' (L' U' B' U B L) F' (U' L' U L)2 F
"""

DS_B = """
(R' U R2 D) (r' U' r D') R2 U (R U R' U R)
U2 (F R' F' R U R U' R') U (R U R' U' R' F R F')
(R U' R' U') M' U (R U' r' U2) (R' F R F')
(f' U' L' U L) (S L' U L U L' U' L F)
U2 (r U' r' F) U F (R U' R' U) (R U' R' F')
U' (R' U' R U') (R' F R U) R' U' F2 U2' F R
(r' U' R U) (r U2' R' U') (R' U R U2) (R' F R F')
U F' U' (L' U2 L U) (L' U' L U') (L U F U' F' L') F
U' (r' U' R U) M' U2 (R U B U' B' R2') U R
(R U R' U' R' F R) (S R U R' U' f')
R' U' F' U F2 R F' U2 (R U' R' U2) F' U F
"U2 (F r U r' U' R U' R' U' r U r') (U R U' R' F')
U l' D (l U' l U2) (l' U l U) (l' U l U') l2' D' l"
"""

DS_F = """
U (L' U' L U) (r' U2' R U) R2' F2 R U r
U2 (R' F R F') (r U' r' U') (F' U' F U) r U2' r'
U' (R' F R U) R' U' F2 U2 F U' (R U R2' F R F') R
U' r U2' R2' F2 r F' R U2' r2' F2 R
U2 (F R U' R' U R U2 R' U' F') U (F R U R' U' F')
r' U2' (R U R') (F U F') (R U' R' F' R) U M'
U' (R' F2 R2 U2' R') (F' R U2' R2' F2 R)
(R U R2' F R F') (R U R' F) (R U R' U') F2 U2 F
U' (r U' r' F) U F U' (R U' R' U) (R U R' F')
"M U (L F' L' U' L) (F' U F) (L' U L) U2 l'
U F U2' (r U' r' U) (R' F R F') (r U2' r' U') F'"
U' (R' U R U') (R' U R U2) (R2' F R F') U F' U F R
(F R U R' U') (R U' R' U R U B' R B R2' F')
"""

DS_L = """
"U (F' L' U' L U) (l' U l U' L' U' L U' l' U l F)
U2 (r D' r2' U') (r U r' U) (r U r' U2') (r U' r D r')"
R U2' R2' U' F' U F R F' U2 F R U' R'
U F U (R U2 R' F) (R U R' U') F' U' (R U2 R' U') F'
U' (F R U' R' U R U R') (S R U R' U' f')
U' (r' U' F' U2) (r U' r' F2) (r U r' U' r)
U' R' U2 (R' F R F') U' (F' U' F U') R
U' (R U R' U2) (F' U' F U2) (R' F R2 U R' U') F'
U2 (R U R' U2) (F' U' F U2) (R U' R' F') U' F R U R'
R U R2' (F' U' F U) R U2 M' U R U' r'
U' (R U R' U) (R U R2' D') (r U' r' D) R2 U R'
"U (F' L F L' U' L' U L) U (L' U' L U L F' L' F)
U2 M' U' (r' F R U2) F U' (R U' R' F')"
(f' U' L' U L S) (L F L' U' L' U L)
"""

DS_R = """
(R' F R F') U' (S R' U' R U R S')
U F' U' F (r U M U2) R' U r U r'
M' U M U (R' F R U) (R' F R F) U' F'
U2 (L' U' B' U B M') (U l U l' U' l F U' F')
U (F' U' L U F U' F' L2') (U L U' L' U' L F)
U2 (F R U' R' U' R U R2') (F' U' F U R U' F')
U2 (F' L F L' U' L' U L) U' f' (L' U' L U)2 f
(R' F R U') (M' U2 r' F') (R F U' F')
U (F R' F' R U2 R U2' R') U (L' U2 L U2' L F' L' F)
U2 (R' F R F') U' (r U2 r' U') (F' U F U) r U r'
U F (R U' R' F) (R' F' R U2) (R U' R' U) (R U' R' F')
U2 f (U R U' R')2 f' U' (R U R' U' R' F R F')
"""

update_all("DS_U", DS_U)
update_all("DS_D", DS_D)
update_all("DS_B", DS_B)
update_all("DS_F", DS_F)
update_all("DS_L", DS_L)
update_all("DS_R", DS_R)


DSpU = """
U2 (R' U' F' U F R) (F R U R' U' F')
U2 (R' U' F' U F R) (f' U' L' U L f)
(r U R' U R U2' r2') (U' R U M' U' R' U R)
U' (f R U R' U' f') (R' F' U' F U R)
U' (R U R' U' M' U R U' r2') (U2' R U R' U r)
(R U B U' B' R') (f U R U' R' f')
(r U R' U R U2' R') (U' M U2 M' U' M)
U' (F R U R' U' F') (R U R' F' U2 F R U' R')
(l' U' L U' L' U2 l) f (U R U' R')2 f'
U f' (L' U' L U)2 f (r U2' R' U' R U' r')
(MR U R' U) (r U2' r' U) M'
U2 (F R U' R' U2' R U R' F') U (R' U' F' U F R)
"""

DSpD = """
U' f (U R U' R')2 f' (R B U B' U' R')
U (r U R' U R U2' r2') (U'·R' F R F' U r)
(M' U M U) (R U R' U) (R' F R F') r U2' r'
U' (f U R U' R' f') (l' U2 L U L' U l)
U f' (U' L' U L)2 f (L F U F' U' L')
U2 L U2 F U (R U' R' U') (R U' R' U') F' L'
U F U' (R U R' U') F' U2 (R' F r U') r' F' R
U (F R U R' U') (R U' R' F' U' r' F U' F U r)
U' F' (L' U' L U)2 F (L' B' U' B U L)
U F (R U R' U')2 F' (R' F' U' F U R)
U' (R' U' F' U F R) f (R U R' U')2 f'
U (R U B U' B' R') F (U R U' R')2 F'
"""

DSpB = """
U2 (R U' R2' D') (r U r' D) (R2 U' R' U') R U' R'
U2 R' U F' U F (R U R' F') U F U R
"U2 (F' L F L' U' L' U L) U' (L' U' L U L F' L' F)
U F (R U' R' U') (R U R' U' R' F R F') (R U R' F')"
U2 (R' F R U') (R' U2' R U) R' F2 U F R
F (R U' M' U) (R' U R U2) r' U' (R U R' F')
(f U R U' R') (S' R U' R' U' R U R' F')
(L' U' L U L F' L') (S' L' U' L U f)
U' F U (R U2' R' U') (R U R' U) (R' U' F' U F R) F'
U (F R U R' U') (R' U R U2 r' U r U F' r' U' r)
U' (r U R' U') (M U2 R' U') F' U F R2 U' R'
U (R U2' R' U) (R U R' F) (R' F' R2 U2') (R2' F R F')
"U2 (F' l' U' l U L' U L U l' U' l) (U' L' U L F)
"""

DSpF = """
U2 r' U' (R' F2 R2 U' R' U2) r U' r' F r
U2 (R U B U' B' R') (F U R U2' R' U' R U R' F')
U2 (R' F R F') U' (F R' F' R2 U' R2) U' F' U F R
U' (r U r' U2) (r U' r' F) (R U2' R' U2) (r U2 r' F)
U (r U2' R2' F2) (r F R U2') r2' F2 R
l U2 (L' U' L) (F' U' F) (L' U L F L') U' M'
U (R' F2 R2 U2' R') (F R U2' R2' F2 R)
U2 (R' F R U R' U' F' U R) U' (r' U2' R U R' U r)
U (F R U' R' U' R U R') (F2 r U r' U' r' F r)
M U' (R' F R U R') (F U' F') (R U' R') U2' r
(R U2' R' U') (R U R2' F R F') U2' (R' F R F')
U2 (R2' F R F') U' (R U' R2' F R F' R) (U' R' U2' R)
"""

DSpL = """
(L F' L' F) U (S' L U L' U' L' S)
U' F U F' (R' F r U2') (M U R' F' R)
U' (F U R' U' F' U F R2) (U' R' U R U R' F')
U2 (F' L' U L U L' U' L2) (F U F' U' L' U F)
U R' U' F U F' (R U' R' F') R U2 M' U' M
U2 (R U B U' B' M') (U' r' U' r U r' F' U F)
U2 (F R' F' R U R U' R') U f (R U R' U')2 f'
(r U' r' U) (M' U2 R U) (r' F' U F)
U' (F' L F L' U2' L' U2 L) U' (R U2' R' U2 R' F R F')
U2 (R2' F R F') U2 (R' U' F' U F R2) U2' R' U2' R
U2 (F R U R' U') (R U R' U2 R' F R F' R U R' F')
U2 f' (U' L' U L)2 f U (L' U' L U L F' L' F)
"""

DSpR = """
"U' (F R U R' U') (r U' r' U R U R' U r U' r' F')
U2 (l' D l2 U) (l' U' l U') (l' U' l U2) (l' U l' D' l)"
U' R' F' U2 F2 U (R U' R' F') (R U R' U R)
U2 R' U' F' r' U' F U F r U' F U R
"U (F' L' U L U' L' U' L) (S' L' U' L U f)
U' (R U R' U' R' F R F') U2 (R' U' F' U F R)"
F U (R U R' F') U F (R U R' U) F'
U2 (F R U R' U') (R U R' F' U' F' r U r')
U (L' U' L U2') (F U F' U2') (L F' L2' U' L U) F
U (F' U' F U2) (R U R' U2) F' U F (R U R' F') U' F
U' (R' U' R U') R' U' R2 D (r' U r D') R2' U' R
U' (F R' F' R U R U' R') U' (R U R' U' R' F R F')
(f U R U' R' S') (R' F' R U R U' R')
U2 (R' U' R U) (F R U R' U' F') U M U' R' U r
"""

update_all("DSpU", DSpU)
update_all("DSpD", DSpD)
update_all("DSpB", DSpB)
update_all("DSpF", DSpF)
update_all("DSpL", DSpL)
update_all("DSpR", DSpR)


DTU = """
(r' U' r U') R' U (r' F R F') (R' F R F') U r
U (L' U' L U' L' U B' U B L) (F' L' U' L U F)
U' (R U R' U R U' B U' B' R') (F R U R' U' F')
U2 (r' U2' R U R' U r2) U2 (R' U' R U') r'
(r U2' R' U' R U') (r2' U2' R U R' U r)
(r U M U R' U' r U' r2') (U2' R U R' U r)
U2 (r' U' M' U' R U r' U r2) (U2' R' U' R U' r')
U (R' F' U' F U R2) (U2' R2' F R F' R U2' R')
"U' (L F U F' U' L2') (U2 L2 F' L' F L' U2 L)
U2 (F R U R' U' F') (R U2' R2' F R F' R U2' R')"
(R' U' R F R' F' U F R F') (R U R' U' R' F R F')
U' (R' F R U2) (R' F' R U) (r U R' U R U2 r2) F r
U2 F U (R U' R' U) (R' F R F') (R U2 R' F') L' U L
"""

DTD = """
R' U' R F (R' F' U F) (R2 U' R' U) (R U R' F')
U F (R U' R' U') (R U R2' F') (U' F R F') R' U R
U (r U r' U') R2 D (r' U2 r D') R2' U r U' r'
U (R' F' R2 u2') (R' F' R U') (R' U R u2' R')
U (R U2 R' F) U (r U2 r' U') (R U2 R' U') R' F' R
U2 (r' U' R U' R' U2' r) U2 (R U2' R2' F R F' R U2' R')
(r U R' U R U2 r') U' (R U2' R2' F R F' R U2' R')
(r' U' r U') R' U (MR U' R' U) F' U F r
U' F (U R U2' R') (f U R U' R' f') U2 (R U2' R' U') F'
U' R2' F2 (r U r' F) (R2 U' R D) (r' U' r D') R'
(R' F R U) (R U2' R' U) (r U2 r' U') F' R U2 R'
U' (R u2' R' U') (R U R' F) (R u2' R2' F R)
"""

DTB = """
U' (R' F R U) (R' F' R U2') (R F R' U) R F' R'
U' F' U' F (R U R D) (r' U' r D') R' U2 R'
U2 M' U (R U R' U) MR U2' (R2' F R F' r) U r'
U2 F' U' (L U2 L2' U' L2 U' L' U') (L F' L' F) U F
U2 F U (R' U2' R2 U R2' U R U) (R' F R F') U' F'
(R U R' F') U (R' U' F' U F R) U2 F U R U2 R'
U2 (R U2' R' U') F' U2 (R' F' U' F U R) U' F R U' R'
U (R' U2 R' D') (r U' r' D) R U' F' U' F R
U' R' U' F U R U' F2 U F (R U R' F') U' F
U' (F' L F L' U' L' U L) U (r U M U R' U' r U' r')
U' F (r U r' U2 r U) (R' U2' R U') (r' F' U' r' F r)
U2 r' (R' F2 R U') (R' F2 R2 U R' F) (r U' r' F2 r)
"""

DTF = """
U' (R U R' U) (R' U' F' U F R) F' U2 F R U' R'
(R U2' R' U2 R' F R F') (R U R' F' U2 F R U' R')
U F' (r U r' U2) r' F2 U2' (R U R' U) r
(R U2' R' U2 R' F R F') (L' U' B' U B L)
(L' U2 L U2' L F' L' F) (R U B U' B' R')
(L' U' L U L F' L2' U' L U F) (L F U F' U' L')
(R U R' U' R' F R2 U R' U' F') (R' F' U' F U R)
(R U R' U' R' F R F') (r' U2' R U R' U r)
(F R U2 R') F (R U R' U')2 F' U F'
U (F R' F' R) U2 (R U' R' U2) (F' U' F U') R U' R'
(R' F R F') U2 F' U F2 (R' F' R2 U' R')
U' (F R' F' R) U2 (R U' R' U) F2 (r U r' F)
"""

DTL = """
U' (S' R U R' S U') (R' F R F')
"(F R' F' R U R U' R') (L F U F' U' L')
 (F R' F' R U R U' R') U' (F R U R' U' F')"
U2 R' U2' (F R U R' U' F2) U2 F R
U r B U' B' R' U2 (M U' r U r')
U2 (R2' F R F') (R U2' R2' F R F') (R U' R' U' R)
U2 R' U' F U R2 U' R' F' U (R U R2' F R F')
U2 (M' U' M U2) (r U' r' U2) F' U2 F
"U (R' U' F' U F R) (L F' L' U' L U F U' L')
U2 (F' U' L' U L F) U' (L F' L' U' L U F U' L')
U (R' U' F' U F R) U2 (R U R' F' U' F U R U2 R')"
U' (R' U2' R2 U R2' U F R F') U2 (R' F R F')
U' (R' F R U R') F2 (D R2 U2' R2' D') F R
U2 (M U r U2') (M U' R' U') (R' F R F') M'
U' (F' U' F U) (r U r' U2) M' U M
"""

DTR = """
(F' L F L' U' L' U L) (R' F' U' F U R)
U (S L' U' L S' U) (L F' L' F)
U F U2 (R' F' U' F U R2) U2' R' F'
U' (R' U' F U) (r U2 M U) R' F' R
U F (R U' R' U') (F R U R' U' F') (R U R' F')
U2 (M' U' r' U) F U R' F R U' F' U' R
U2 M' U M U2 (R' F R U2) F U2 F'
"U' (L U F U' F' L') (R' F R U R' U' F' U R)
U2 (F U R U' R' F') U (R' F R U R' U' F' U R)"
U (L U2 L2' U' L2 U' F' L' F) U2' (L F' L' F)
U (L F' L' U' L) F2' (D' L2' U2 L2 D) F' L'
U2 R' U' F' U (L' U L U) F U (R U2 R' U' R)
"U (F U F' U') (l' U' l U2') M' U' M
U' (r' U' F U R U' R' F' r) U2 M U' M'"
"""

update_all("DTU", DTU)
update_all("DTD", DTD)
update_all("DTB", DTB)
update_all("DTF", DTF)
update_all("DTL", DTL)
update_all("DTR", DTR)


DUU = """
U' (R U R' U') (R' F R2 U R' U2) (R' F R F') (R U R' F')
U2 (r U R' U R U2' r2') (U' r U' R' U M U r)
(r' U' R U' R' U2' r2) (U r' U R U' M' U' r')
(R U2' R' F R' F' R2 U2' R') (F U R U' R' F')
U (R U2' R' F R' F') (R2 U2' R2 U') (F' U F R)
(L U L' U L U2 L2) (U' L U' L' U2 L)
(r' U' R U' R' U2') (r2 U R' U R U2' r')
U' (R U2' R' U2 R' F R F') U' (R' U' F U R U' R' F' R)
U' (r U R' U R U2' r') U' f (U R U' R')2 f'
U r2' F2 R2 U2' (r' U r U2') R2' F' r U' r
U' (F U R U' R' F') (R' F' U' F U' R U R' U R)
U (F' U' L' U L F) (L F U F' U L' U' L U' L')
"""

DUD = """
U r' U' (R' F R F') (R' F R U) r F U' F'
U' (r U2' r' U2) (R' F R F') U' (F' U' F U) r U r'
U2 (R D r' U' r D' R') U' (R2' F R F' R)
U (r' U' F' U F r2) (U R' U R U2 r')
"U' (l U F U' F' l2') (U' L U' L' U2' l)
(R U R' U) (R' F R F') U2 M' U R U' r'"
U (r' U' R U M') U' (R2' F R F' U R)
"U' (l U L' U' M') U (L2 F' L' F U' L')
U' (R U B' R B R2') U' (M' U R U' r')"
U' F(S' R U' R' S) (R U2' R' U') F'
"U F'(S L' U L S') (L' U2 L U) F
U F (U R U2' R') (S' R U R' S)F'"
U' (R U2' R') (F U' F') (r U' r' U) (R' F2 R U F)
U (l' U2 L U L' U l2) (F U F' U' l')
U' (r U2' R' U' R U' r2') (F' U' F U r)
"""

DUB = """
U' (R' F R F') U' (R' F R F') (R U2' R') (F' U' F)
"U (L F' L' F) U (L F' L' F) (L' U2 L) (F U F')
U' F (R U' R' U) (R U2' R') (F' U' F') (r U r')"
U' (R' F R U R' F' R F U' S) (R U R' U' f')
(R U R2' F' U' F U R) U2' (R' F R F')
(L' U' L2 F U F' U' L') U2 (L F' L' F)
F U (R U' R2' F') U' F R F' R' U R
U' R' U' F' U F2 (R U R' F') R F U' F'
(F R U R' U' F') (R U2' R' U2 F' U2 F U R U R')
U' (R2' F R F') (R U B U' B' R') U2 (R U' R' F') U F R
(F R' F' R) U2 (R' U' F' U F R2 U' R')
(F' L F L') U2' (L U F U' F' L2' U L)
(R U2' R') (F' U2 F) (R U' R2' F R F')
"""

DUF = """
U' (R B U B' U' R') (F' L F L' U2' L' U2 L)
"U (R' U' F' U F R) (F U R U' R2' F' R U R U' R')
U (↑R' U R U') R2' F (R2 U R' U') F2 U' F U R"
"U' (L U F U' F' L') (F' U' L' U L2 F L' U' L' U L)
U2 (r U' r' U) M' U (R U' R' U2) M F' U F"
U' (M U' R' F2) (R U R' F2) r U F U' F'
U2 (R' F R U2) F U2 (R U' R' F') U' R' F2 R
r' U' (R U' R' U2') F2 (r U2 r U' r' F)
U' (R U R2' F R) F2 U' F U2 (F R' F' R)
F' (r U' r' F2') U' (R U R' U2) (R' F R F')
"""

DUL = """
U' (R U2' R' U') (R' F' U' F U R) U2' (R' F R F')
U2 (F R' F' R U2 R U2' R') (r' U' R U' R' U2' r)
U' (R U R2' U') R' F (R2 U' R' U2') F R F' (R U R' F')
"U2 (F' L F L' U' L' U) (B' U' B U L)
U2 (F' L F L') U2 (F' L F L') (U L' U L)"
U' (R' F' U' F U' R) U2 (R f' U' f)
"U' (L' U L2 D l' U' l D') (L2' U2 L U' L' U2 L)
U (R' U R2 D r' U' r D' R2') (U2' R U' R' U2' R)
(R' F R U R' F' R F U' F') U2 (R' U' F' U F R)"
U' (R' F R U R' U' F' U R) (F U R' F R F' U' F')
(F U R U' R' F') U (F U R U2' R' U' R U R' F')
U' (R U2' R' U') (R U R') (F' U2 F) (R U' R2' F R F')
U2 (F' L F L' U' L' U L) U' (f U R U' R' f')
U2 F (R U' R' U') (R U' R' F') U F (R U R' U) F'
U' (R' F R F') U (R U R2' F R F2') U2' F
"""

DUR = """
U2 (F' L F L' U2' L' U2 L) (l U L' U L U2 l')
U' (R U R' U) (R U R2' D') (r U r' D) R2 U R'
U' L F (R U2' R' U R' U2' R2 U R2' U R) F' L'
"U2 (F R' F' R U R U') (B U B' U' R')
U2 (F R' F' R) U2' (F R' F' R) (U' R U' R')"
U' (R f R f') U R' U2' (R' F R F')
"U (R U' R2' D' r U r' D) (R2 U2' R' U R U2' R')
(L F' L' U' L F L' F' U F) U2' (L U F U' F' L')
F (R U R' U2') (R U2 R' F') U' F U (R U R' U) F'"
U' (R' U' F' U F R) (r U R' U' r' F R2 U R' U' F')
F (R U R' U2') (R2 B U B' U' R') U' R' U F'
"U (L' U2 L U) (L' U' L) (F U2' F') (L' U L2 F' L' F)
(r' U2' R U R') (F U F' U') (R' F' R U) r"
U2 (F R' F' R U R U' R') U2 (R' F' U' F U R)
U2 F U (R U2' R' U) (R' F R F') U' F' L' U2 L
(F R' F' R) U' F' U' F2 R' F' R2 U2' R'
"""

update_all("DUU", DUU)
update_all("DUD", DUD)
update_all("DUB", DUB)
update_all("DUF", DUF)
update_all("DUL", DUL)
update_all("DUR", DUR)


E_U = """
(r U R' U R U2' r') U' (R' U2' R U R' U R)
M' U' (R' U2' R U R' U' R U R' U R)M
U F U (R U' R2' F R F) (r U r' U) r' F r
(S' R U R' S) U (R U' R' U R U2' R')
U2 (R' U' R U') R' F U F' (R' F R U') F' U2 R
(r U R' U R U2') (M U R' U R U2' R')
(l' U' L U') (L' U L U') L' U2 l
U' r' U2' (R U R' U') (R U R' U) r
U' M U (L' U' L U' L' U L U' L' U2 L) M'
"U R U' R' (L' U' L U' L' U2 L2) (F' l' U' l F L')
U2 (MR U R' U R U2' R' U M') U' (R U R' U R U2' R')"
U' r' U' (M' U' R U) (R' U' R U) r' U r
"U' (L f' L' U' L f) (L2' B' R B L)
U R' U MR U (R' U' R U') M'R' U' R"
"""

E_D = """
U' (L' U2 L2 F' L' F L' U2 L) U (L' U' L U' L' U2 L)
U' (R U2' R2' U' R2 U' R2' U) (R' F R F' U R)
(R U R U') R' F U R U' (R F' R' U) (R U' R' U R)
U (R' U2' R U) (R2' F R F') U F2 (r U r' F) R
U' (f' L' U' L U f) (L' U2 L2 U L2' U L2 U2 L')
U (R U R' U' R' F R F2') (L F L' U' L' U L)
U' (R' U2' R2 U R2' U R2 U2' R') (F U R U' R' F')
U (R U R' U R U2' R') U2' (R U2' R2' F R F' R U2' R')
"U2 (R' U' R U2') (F R' F') U2' (F R F') (U2 R' U R)
U (L U2 L' U' L F U' F' L') F' (L' U' L U)2 F
U2 (r' F R U) F (R U' R' F') U' (R' F R F') r U R'"
U2 (R U R') (F' U' F) (R U R' U2) (R' F R2 U R' U') F'
U' (f' U' L' U L S) (U' L' U L)2 F
(F l' U l F2) (l F' L' F) l' U2 L
"""

E_B = """
U (R' U' R U' R' U2' R) U (R' F R U R' U' F' U R)
U (R U R' U' R' F R F') U' (F R' F' R U R U' R')
(R U R' U') (R' F R2 U R') d (R' U' R U' R')
F (R U2 R' U') (R' U2' R U R' U R2) U R' U' F'
(F U R U' R' F') (R' F' r U R U' r' F)
U (R U' R' U) (f R U R' U' f') (R' F R F')
(r' F R F') (r U' R' U2) (R' F R F')
(L' U2 L2 F' L' F) (L' U L U) (L F' L2' U' L U F)
(F R U R' U' F') (R U R' U' R' F R F')
"(L' U2 L U2' L F' L' F) (R U R' U R U2' R')
↓ F (l' U l F2') (L2' D' l U2 l' D L2)"
"(L' U2 L2 U L2' U L2 U2 L2') (U' L U L F' L' F)
U r D' (R U2' R' U2) (R U' R' U') (R U R' D) r'"
F U (R U' R' U) (R U2' R' U) (R U R' F')
"""

E_F = """
U' R' U F' U F (R U R' U R U2' R') U' R
U2 (f R U R' U' f') (r U R' U' r' F R F')
F (R U R' U') (R U' R' U) (R U R' F')
U (L' U L2 U F U' F' L') U' (L F' L' F)
"(L' U2 L U L' U L2) (F' L' U' L U F U' L')
F (R U' R2' F' R) (U2 R U2' R') (F U' F')"
U' R' F' U2 (R U R' U) R2 U2' (R' F R U2 R')
U2 (F' U' L' U L f) (R U R' U' R' F R f')
U2 (R U' R' U') (F U R U' R' F') (R U' R' U) R U2' R'
U2 (R' U' R U) (R U2' R' U2) R' U2' F R F'
U (L U L' U L U2 L') (F R' F' R U R U' R')
U2 (F U R U' R') (U2 R' F' U' F U R2 U2' R' F')
(f' L' U' L U f) (L U F' U' L' U L F L')
"""

E_L = """
(R' U2' R U) R' F U F' R U F U' (R U' R' F')
U F' U' F (R U R' F) (R' F' R U') (R' F R F')
r U2 (L' U2 L U L' U L) U' r' (F R' F' R)
U2 x' U' R' F (R2 U' R' U) r' F U' (R' F R U) r x
U' (r U' r' U') (r U r' U') (R U' R' U') (F R' F' R)
U' (R U R' U R U2' R') U' (F' L F L' U' L' U L)
(L F' L' F l' U' L U L') (U2 L U L' U l)
U' (r U R' U R U2' r') U' (F' L F L' U' L' U L)
"(L' U' L U') (L' U' L U) (F U2' F' U2) (L' U2 L)
U (r U M U R' U' r U' r') (F R U' R' U R U2' R' U' F')"
U' (R' U2' R U R' U2) (F R' F' R) F' U2 F U R
(L F' L' U' L F L' F' U F) (l' U2 L U L' U l)
(R' U R U2) (R U2' R' U') (R U R' U2) (R' U2' F R F')
"""

E_R = """
U (R' F R F') U' (F R' F' R2 U' R')
U↑r' F U (R' F R2 U' R2' F' R) U' r
U' (R U' R' U) (R U' R' U2) (F' U F) (R U R')
U2 F' (r U r' U') r2 F r U2 F U r
(F R' F' R U R U' x'M') (U2 L' U' L U' L')
(L' U' L U' L' U2 L) (F' L F L' U2' L' U2 L)
(F R' F' R U2 R U2' R') U (R' U2' R U R' U R)
(r U' r' U2) (M' U' R U r' U2') (F R' F' R)
F' (r U R' U2) (L' U L U') (r U' r' F) r' F2 R
(S' R U R' S) U (R U r' F R' F' r)
"(l' U' L U' L' U2 l) (F' L F L' U2' L' U2 L)
(R U2' R' U2 R' F R F')2"
U2 (↑ l F U' F' U l') U' (L2 F' L' F L')
"""

update_all("E_U", E_U)
update_all("E_D", E_D)
update_all("E_B", E_B)
update_all("E_F", E_F)
update_all("E_L", E_L)
update_all("E_R", E_R)

CUBEROOT_ALLL = """
"x· R2' D2 (R U R' D2) R U' R x'
 U↑ l U' l B2 l' U l B2 l2'
 x2 l2 B2 x (l F l' D2) l F' R
 U x R D' (l F2' l' D) l F2' l2' x2
 U x' (R U' R D2) R' U R z' R2 U2' x
=U x' (R U' R D2) (R' U R D2) R2' x
U2 R' D' (R U2 R' D) (R U R' D') (R U R' D) R
U2 x'·L2' D2' L U L' D2' L U' L x
U' x·(L U' L D2') (L' U L D2') L2' x'
 x' R' U'D' (R U R' D) (R U' R' U R)"
"x· (R' U R' D2) (R U' R' D2) R2 x'
= x (R' U R' D2) (R U' R' D2) R2 x'
 U↑ l2 B2 l' U' l B2 l' U l'
 U x2 l2 F2' (l' D' l F2') l' D R' x'
x' U2' R2 (U' L' U) R2 (U' L U') x
U x' R2 D2 (R' U' R D2) R' U R' x
U2 x'·(L' U L' D2') (L U' L' D2') L2 x
U' (R U R' F') (r U R' U') (r' F R2 U' R')
U' x·L2 D2' (L' U' L D2') L' U L' x'
 U' f' U f' R2 f U' f' R2 f2"
"x'· (R U' R' D) (R U R' D') (R U R' D) (R U' R' D') x
U (R' U'D' R' D) (F D' R UD) (R U' R' F' R)
 x (l B' l' U) (l B l' U') (l B l' U) (l B' l' U') x'
 x' (l F' l' D) (l F l' D') (l F l' D) (l F' l' D') x
 U (R' U' R' U) (L U' R U L' U') R F (R' U R U') F'
 U F R' F' (r U R U') (r2 U' R U) (r f' U' f) x'
 (R U R' U) (R' U' R F') (R U R' U') (R' F R2 U' R2' U R)
 R'L' B' (L F' L') B RL B' (R' F R) B
 U R U' L D2' L' U M' x' U' R D2 R' U L'"
"(R' F R f') (R' F R2 U R' U') (R' F' R2 U R') S
U2 (L F' L' f) (L F' L2' U' L U) (L F L2' U' L) S'
S (R' F R f') (R' F R2 U R' U') (R' F' R2 U R')
U' (R' U R U') (R2' F' U' F U) (R F R' F' R2)
R' U' F' (R U R' U' R' F R2 U' R' U' R U R') U R
U' (R' U R U') (R2' F' U' F U) (R F R' F' R2)
U (R' U2 R' d') (R' F' R2 U' R' U) (R' F R U' F)
 (R2' F R F') R' U' F' U F (R2 U R' U' R) 
 R2 B2 R2' L U' L F2 R' D L' F2 M x
 U M U2' r' U l' U2 r U' M'R' U2 R2 x'"
"(L2 u L' U) (L' U' L u') (L2' f' L f)
U2 R2 U (R' U R' U') (R U' R2 U'D) (R' U R D')
= U2 R2 U (R' U R' U') (R U' R2 U'D) (R' U R u'
U2 (R2' U' R U') (R U R' U) R2 UD' (R U' R' D)
U2 (R2 u R' U) (R' U' R u') (R2' F' U F)
U2 (R2 u R' U) (R' U' R u') (R2' F' U F)
 U RL U2 R'L' y' R' U L' U2 R U' L
 U2 R2' S2 U R2 D' R2' D B2' U' F2 r2"
"(f' L' f) L2· u (L' U L U') L u' L2'
U2 F' U' F (R2 u R' U) (R U' R u') R2'
=U2 F' U'↓F (R2 u R' U) (R U' R u') R2'
=U R' d' F (R2 u R' U) (R U' R u') R2'
=U R' U' R y (R2 u R' U) (R U' R u') R2'
U (R' U' R UD') R2 U R' U R U' R U' R2' D
U (↓L' U' L UD') (L2' U L' U) (L U' L U') L2' D
 R' U L' U2 R U' L y RL U2 R'L'
 U2 R2' F2 U R2 D' R2' D B2' U' S2 r2"
"(R2' u' R U') (R U R' u) (R2 f R' f')
= R2 u' R U' R U z' U' R f2' U R' U' z'
=(R2 u' R U') (R U R' u) R2 y R U' R'
↓L2' U' (L U' L U) (L' U L2' UD') (L U' L' D)
 U2↑R2' F2 (R U2 R U2') R' F (R U R' U') R' F R2
 U' L'R' U2 LR y L U' R U2 L' U R'
 R2' S2 U' R2 D R2' D' F2 U B2' r2"
"(f R f') R2'·u' (R U' R' U) R' u R2
(R U R' U'D) (↓R2 U' R U') (R' U R' U) R2 D'
(↓R U R' U'D) (R2 U' R U') (R' U R' U) R2 D'
=D' (↓R U R' U'D) (R2 U' R U') (R' U R' U) R2
R U R' y' (R2 u' R U') (R' U R' u) R2
U2 F U F' L2 u' L U' L' U L' u L2
 U' L U' R U2 L' U R' y' R'L' U2 RL
 R2 B2 U' R2' D R2 D' F2' U S2' r2'"
"(M2' U M2') U2 (M2' U M2')
= (M2 U M2) U2' (M2 U M2)
M2 U2 M2 U' M2 U2 M2
M2 U2 M2 U M2 U2 M2
 R2' U2' R U2' R2 U2' R2' U2' R U2' R2
 RL U2 L'R' y L'R' U2 RL
 R2 S2' R2' U' R2 S2' R2'"
"(R U R' F') (R U R' U') (R' F R2 U' R')
U (R U R2' F' R) (U R U' R') (F R U' R')
 (R U' F U') (R' U' R U) F' U2' R'
[oh,key] (R U2' R' U') R U2' (L' U R' U' r) x'
 L (R U2' R' U') R U2' (L' U R')
"(L' U' L F) (L' U' L U) (L F' L2 U L)
U' (L' U' L2 F L') (U' L' U L) (F' L' U L)
x (↑R2' F R F' R U2') (r' U r U2') x'
=(M'R' F R F' R U2') (r' U r U2' r')
 (R' U2' R U R' U2') (L U' R U L')
[oh,key] U' (R' U L' U2) (R U' R' U2) R r x'
=z D' (R U' R2' D) (R' D' R2 UD) z'
D (R2' D' R2 U) (R D R' D') (R U' R' U R')
U r' F R' F2 (r U' r' F2) r R
U z U' R D' R2' U R' U' R2 UD z'
U L' U R' U' U' z U R' U' R2 UD z'
 U2 z U' R2' U R U' R2 z' R U' L U R'"
"(R F U' R' U R U F' R2') (F' R U R U' R' F)
 z (U x' l' D x' l2' B' l D')2 z'
 z U R' D (R2 U' R UD') R' D (R2 U' R D') z'
= (L U' R U2' L' U R')2
 (R U R' U) (R U R' F' R U R' U' R' F R2 U' R' U2) R U' R'
(f R' F R2 f') U (S R' F R2 B' R F') z'
 R2 U2' B2 U R2' U2' R2 B2 U B2 U2' B2 R2'
 R2 UD R2 U2D' FB R2 D2 FB' U' L2 D2 F2"
"(r' D' F r U' r' F' D) (r2 U r' U' r' F r F')
=(L' F' U L U' L' U' F L2) (F L' U' L' U L F')
= (R' U R U') (R' F' U' F) (R U R' F) (R' F' R U' R)
 z (D' x l U' x l2 B l' U)2 z'
 z U' R D' (R2 U R' U'D) R D' (R2 U R' D) z'
= (L' U R' U2 L U' R)2
R' U L' U2 R U' R'L U L' U2 R U' L
(R' U R U') (R' F' U' F) (R U R' U') R U' f R f'
(f' L F' L2' f) U' (S' L F' L2' B L' F) z
 R2' U2' F2 U' R2 U2' R2' F2 U' F2 U2' F2 R2
 L2 U'D' L2 U2D F' B' L2 D2 F'B U R2 D2 F2"
"(L U2 L' U2') L F' (L' U' L U)· L F L2'
U (R U R' F') (R U2' R' U2') (R' F R U) R U2' R'
(R U' R2' D') (R U R' D) R U' (R U' R' U R U R')
(R U2' R2' F R F') (R U' R') (F' U F) (R U' R')
 (L U2 L' U) (F R' F') L F R F' U L'
 U' F U2 S R B' D' F R2' F2 R' F D z'
 U2 L'R U2 F' U2 L'R' U' LR F LR U' R2"
"(R' U2' R U2) R' F (R U R' U')·R' F' R2
(R' U2 R' D') (R U' R' D) (R U R U') R' U' R
U (↑R2' F R U R U' R' F') (R U2' R' U2 R)
 U' (R' U2' R U') F' L (F R' F') L' F U' R
 U F R U' R2' U2' R F' r' F M' U2' R
 U2 RL' U2 F U2 RL U R' L' F' R'L' U L2"
"(R U R' U') (R' F R2 U' R' U') (R U R' F')
(R U R' U') (R' F R2 U' R' U) (F' L' U L)
U2 (L' U' L U) (L F' L2 U L U) (L' U' L F)
R2' u' R2 u R2' y R2 u R2' u' R2
 R2' D' F2 D R2 B2 D r2' U' F2"
"R2 U' S' U2' S U' R2
U M2 U M U2 M' U M2
U' M2 U M' U2 M U M2
U' (R U R' U) (R' U' R2 U') (R' U R' U R)
U2 L2 U' L2' S' L2 S U L2'
 U (↓R U' R U) (↓R U R U') R' U' R2
  U' R2 U' (R' U' R U) (R U R U' R)"
"L2 U' S U2' S' U' L2
U' M2 U' M U2 M' U' M2
U z U2' R U R U' R' U' R' U' R U' z'
U' z U' (R U' R' U') (R' U' R U) R U2' z'
U (↑R' U R' U') (R' U' R' U) R U R2'
U M2 U' M' U2 M U' M2
U2 R2' U R2 S R2' S' U' R2
U'↑R2' U (R U R' U') (R' U' R' U R')
M2 u M' u2 M' u M2
U z U2' R U (R U' R' U') (R' U' R U') z'"
"(↑R' U R' d') (R' F' R2 U' R' U) (R' F R F)
=U↓ x (U' f R' f') (R' F R' F' R2 U') (R' U R U) x'
 (R' U R U') R' f' U' (R U2 R' U' R U' R') f R
 U (F' U F' U') (R' F' R2 U' R' U) (R' F R F)
(↑R' U R' U') (R D' R' D)·R' UD' (R2 U' R2' D) R2
U (↓R U' R U) (R' D R D') R U'D R2' U R2 D' R2'
U2 (R' U' F'S U F2 U' B') (R2 U' R' D R' U) z'
(R' U R U') R' f' U' (R U2 R' U' R U') R' f R
U' (F U' F U) (L F L2 U L U') (L F' L' F')
U2 R b (R' U' R U' R' U2 R) U' b' R' U' R U R'"
"(f' U f R' U' R' U R2) (U R' U' R' F R F')
U (F R U' R' U' R U R' F') (R U R' U' R' F R F')
U (F R' F' R U R U') (R2' U' R U R B' R' f) z'
 U R2 U' (R' U R U') f' y' U' (R U' R' U') z U R x
=U R2 U' R' U R U' x' U' z' U' R U' R' U' z U R x
U F R' F (R2 U' R' U') (R U R' F') (R U R' U') F'
U' f U (R U R2' U'D') (R U R' D) R2 U2' B' z'
 U F (R U' R' U') R d (R U R' B') R U' R2
 U (R2 U' R2' U' R2 U) F U F' (R2' F U' F')"
"(M2' U2 M U) (M2' U M2' U M)
 U M' U' M2 U' M2 U' M' U2' M2
(R2 U' S' U2' S U' R2) U' (R2 U' S' U2' S U' R2)
 (R' U' R U') (R U R U') (R' U R U) R2 U' R'
U (M2 U2' M U') (M2 U' M2 U' M)
 U x' (R U' R' U) D R' U'D (R' U R) D2 x
U' (M2 U M2 U) (M' U2 M2 U2 M')
 U (S M2 S') (u M2 u' M2)"
"f (R' F2 R S') (R' U' F U) (r U2 R U') r'
U'↑R2' F' (R U R' U') (·R' F R2 U' R' U2) (R2 U R' U R)"
"(L' U L U') F (R' F R F2') (L F' L' F)
U'↓F2 R U' R' U' R U R' F' R U R' U' R' F R F2'
 U2 F R U R' U' R2 U' R' U R U R F' U R' U' R"
"(R U' R' U) F' (L F' L' F2) (R' F R F')
R' (F R U' R' U' R U R' F' R U R' U' R' F R F') R"
"(F U R U' R' S) (U f' R' f R U' R' f' R)
U↑R' U (R U R' F' R U R' U' R' F R2 U' R') (U2 R U' R' U2 R)"
"U' (r U R' U' r' F R2) (U' R' U' R U2' R' U' F')
U'↑S' (R2' F R F' R U2' R' F' U2'↓F R) S"
"U (l' U' L U l F' L2') (U L U L' U2 L U F)
U↑S (L2 F' L' F L' U2 L F U2↓F' L') S'
 F R U (R U2' R' U') (R U' R' U2) (R' U2' R U') R' U' F'"
"U (F U R U2' R' U R U R2') (F' r U R U' r')
S' (R' F' U2' F R U2' R' F R' F' R2) S"
"U' (F' U' L' U2 L U' L' U' L2) (F l' U' L' U l)
S (L F U2 F' L' U2 L F' L F L2') S'"
"x' (· R2 U2' R' U2 R' F R F') (L F' L' F) l'
 R F U R' U2 R' U' R U R F' R U R U' R2"
"x' (·L2' U2 L U2' L F' L' F) (R' F R F') r
 R U R U' R2 U' R F U R' U2 R' U' R U R F'"
"U2 (R B R' F R B' R2') (F' r U R U' r')
 U' (R' U' R F) (R' U R U') (R' F' r U R U' r')
U (l' U' L U l F' L' F) U (F l' U' L U l F' L') (wyh)"
"U2 (L' B' L F' L' B L2) (F l' U' L' U l)
 U' (r U R' U') (r' F R U) (R' U' R F') R' U R
U' (r U R' U' r' F R F') U' (F' r U R' U' r' F R) (wyh)"
"R U R' L'· U2 (R U' R' U') R U' M'x'
(S' R' U' R S) (R' U F' U' F U R)"
"L' U' L R·U2' (L' U L U) L' U M'x'
(S L U L' S') (L U' F U F' U' L')"
"U' (R' U' F R' F' R2) (S' R' U R S)
U (L' U2 L2 F' L' F) U (S L' U L S') (wyh)
 U' (R' U2' R) F U' (R' U R U) (R' U R U') F'"
"U (L U F' L F L2') (S L U' L' S')
U' (R U2' R2' F R F') U' (S' R U' R' S) (wyh)"
"U'↓F R (S U S') R' S U' f'
= R' F' (M U' M') F M U r
U (F U R U' R' F') (R U R' U' M' U R U' r')"
(R' U2' R) (F U' R' U' R U F')
(L U2 L') (F' U L U L' U' F)
U' (F U' R' U R U F') (R' U2' R)
U (F' U L U' L' U' F) (L U2 L')
"M U' M' (F R U R' U' F') M U M'
U' (R' U' F R' F' R U2' R) (S' R' U' R S)
U (F R U R' U' F') (R' F R2 B' R2' F' R2 B R')"
"M U M' (F' L' U' L U F) M U' M'
 U2 M U' M' (F U R U' R' F') M U M'
U' (F' L' U' L U F) (L F' L2' B L2 F L2' B' L)"
"U2 f (U2' R2' U2 R2) (U' S R2' S' U' R2) f'
F (U R U2' R' U R U R')2 F'
 F (R U' R' U' R U2' R' U')2 F'"
"U2 x· R2' D2 (R U2 R' D2) R U2 R x'
x'·L2' D2' (L U2' L' D2') L U2' L x"
x'· R2 D2 (R' U2 R D2) R' U2 R' x
"U (↑B U' B' R') (f' R U R' S) (U' R' F R2)
U (L U2 L' U' L U' L) (D' L U2' L' D L U2' L)
(R U R' U) (R U' R' U2) (R' D' R U2 R' D R2 U' R')
 U2 (F R U' R' U' R U2' R' U' F') (R U R' U R U2' R')"
"U' (↑B' U B L) (f L' U' L S') (U L F' L2')
 U' (R' U2' R U R' U R') (D R' U2 R D' R' U2 R')"
"U' (F l' U' L U l F' L2') (U' L U' L' U2 L)
 U (R' U' R U') (R' U R' U) L (U' R U R) L'"
"U (F' r U R' U' r' F R2) (U R' U R U2' R')
 U (R U R' U) (R U' R U') L' (U R' U' R') L"
"r' D' F (r U r' F2) (r U r') D r
 (↑R' U2 R U R' U) (R' D' R U' R' D R U R)"
"R F U' (R' U' R U2') (R' U' R) F' R'
(↑ L U2' L' U' L U') (L D L' U L D' L' U' L')"
"(L U L') (F' U L U L' U' F) (U' L U' L')
 U2 (R U R' U') L' U2 (R U R' U2) L (R U' R')"
(R' U' R) (F U' R' U' R U F') (U R' U R)
"U2 (R U' R2' F R U) (R U' R2' F' R U') (F' U F)
 U2 R U'D' (R U2' R' U) (R U R' D) (R' U2' R U' R')"
(F R U' R' U R U R') (U R U' R' F')
"↑R2' D' (r U2 r' D) R U2 R
 U2 (R U' L U') (R' U L' U2) R U' R'"
"↑R2' D' (R U2 R' D) R U2 R
U2 L2' D' (L U2' L' D) L U2' L"
"(L U L' U L U2 L2') (U R U' L U R')
U2 R' F (R U R' F') M U' (F2 U F) r"
U (R' U' R2 D) (R' U' R D') R2' U2' R
"U (FS' R U' R' f R' F' R U2) (R U' R' F')
U'↑R2' F' (R U2 R U2') R' F U' (R U R' U' R)
U (R U r' F R' F' r) U' (R U R' U R U' R')
 U R U L' U R' U' L U' R U R' U R U' R'"
"U (R f R' f') U' (R2' u' R U' R U R' u R)
(R D r' U2 r D' R') U2 (R' U R U R' U R)
U2 (↑R2' F2 R F') (L F L' F) M' U (r' F R2)
U2 (F' L F L' U' L' U L) U (↑ L U L F' L' F U' L')
 U' R' U R U R' U2 R U2 y R U' R' U2 R U' R'"
"U (R B R' U2') (R B' R2' D2) (r U' r' D2) R
 (R U' R' D) (R' U' R D') (R2 U R' U') R' U2 R'"
"U2 (L2' U S U2 S' U ) (D' L U2' L' D L U2' L)
(↑R2' D' R U2 R' U'D) (R' U' R2 U R U R2')"
"U2 (L' U R U' L U x'M') (U L' U L U2 L')
U2 S' (L' U L U F U2' F' U' L' U L) S
U2 S'F (l' U2 L U') (L' U2 l2 F2' l') S
(R U' R' U') (R U R' U) (R U R2' F' R U R U' R' F)"
(R' F' r U2) (R' D R U' R' D' R2) (U' r' F)
"U' (L' U' L) (U' L' U L)2 U (l F' L' F M')
U (↓R2 U' R2' U' R U2D') (R U' R' U'D) R U R2'
↓F U (R U' R D) (R' U' R D') R2' U (R U R' F')
U' F (R U R2' F R F') (R' U2' R2 U R2' U) R F'"
"(L U2 L' U') F L UD' (L' U' L U'D) L' F'
U' (R' U R U') (R' U' R U2) (R D R' U' R D' R2' U' R)
U (L' U L U') (L' U' L U2') (L D L' U' L D' L2' U' L)"
"U2 R2 D (r' U2 r D') R' U2 R'
↑ L2 D (l' U2' l D') L' U2' L'"
"↑ L2 D (L' U2' L D') L' U2' L'
 U2↓R2 D (R' U2 R D') R' U2 R'"
"(R' U' R U' R' U2' R2) (U' L' U R' U' L)
U2 L F' (L' U' L F) M U (F2' U' F') l'
U2 (r U' r' U' r U r') (F R' F' R U R U2' R')"
"U (R U R2' D') (R U R' D) R2 U2' R'
U' (L U L2' D') (L U L' D) L2 U2 L'"
"U' (F'S L' U L f' L F L' U2') (L' U L F)
U↑L2 F (L' U2' L' U2) L F' U (L' U' L U L')
U' (L' U' l F' L F l') U (L' U' L U' L' U L)
U' (R U R' U) (R U' R' U) (F' R U2' R' U2 R' F R)
 U (R' U' L U') (R U L' U) (R' U' R U') R' U R"
"U' (L' f' L f) U (L2 u L' U L' U' L u' L')
U2 (R' D' r U2 r' D R) U2 (R U' R' U' R U' R')
U2 (↑ L2 F2' L' F) (R' F' R F') M' U' (l F' L2')
U2 (F R' F' R U R U' R') U' (↑R' U' R' F R F' U R)
 U' R U' R' U' R U2 R' y' U2 R' U R U2 R' U R"
"U (R' F' R U2') (R' F R2 D2) (r' U r D2) R'
 (R' U' R U) (R U R' U') R' U F R U R U' R' F'"
"U2 (R2 U' S' U2' S U') (D R' U2 R D' R' U2 R')
(↑ L2 D L' U2' L UD') (L U L2' U' L' U' L2')
U2 (R U2' R' U) (R U R2' D' r U2 r' D R2 U' R')
 (↓R2 D R' U2 R UD') (R U R2' U' R' U' R2')"
"(r U R' U2') (L D' L' U L D L2'x') (F R F')
 U' (R U2' R2' D') (R U2 R' D) (R2 U' R' U2) R U2' R'"
"U2 (R U' L' U R' U' x'M') (U' R U' R' U2' R)
U2 S (R U' R' U' F' U2 F U R U' R') S'
U2 SF' (r U2' R' U) (R U2' r2' F2 r) S'"
"U (R U R') (U R U' R')2 U' (r' F R F' M')
U' (↓L2' U L2 U L' U2D) (L' U L UD') L' U' L2"
"(R' U2' R U) F' R' U'D (R U R' UD') R F
U' (R U' R' U) (R U R' U2) (R' D' R U R' D R2 U R')"
"U (R U2' R' U' R U' R') (L' U2 L U L' U L)
U' (L' U2 L U L' U L) (R U2' R' U' R U' R')
U (F' R F R2' D' R) U (R' D R2 F' R' F)"
"U2 (R U R' U R U2' R') U (R U2' R' U' R U' R')
U (L' B U B' U B U2 B' L U2) L' U' L"
"U2 (L' U' L U' L' U2 L) U' (L' U2 L U L' U L)
U' (R B' U' B U' B' U2' B R' U2') R U R'"
U (R U2' R' U' R U' R') U' (R U R' U R U2' R')
U' (L' U2 L U L' U L) U (L' U' L U' L' U2 L)
"U' (L' U2 L2 F' L' F) (L' U B' U B L)
 U (R' U2' R2 U R2' U R) U' (R U R' U' R U' R')"
"U (R U2' R2' F R F') (R U' B U' B' R')
 U (R U2' R2' U' R2 U' R') U (R' U' R U R' U R)"
"(R' U' R U' R' U2' R2) (U R' U R U2' R')
U2 (L' U' L U' L' U2 L2) (U L' U L U2 L')"
"(L U L' U L U2 L2') (U' L U' L' U2 L)
 U2 (R U R' U R U2' R2') (U' R U' R' U2' R)"
x' (·R2 D2 R' U' R D2 R2') (D R U R' D') x
"(L U L' U) (L' U2 L2 U L2' U L2 U' L')
U2 (R U R' U) (R' U2' R2 U R2' U R2 U' R')"
"(R' U' R U') (R U2' R2' U' R2 U' R2' U R)
U2 (L' U' L U') (L U2 L2' U' L2 U' L2' U L)"
"U2 F (R U' R' S U') (R U f' U) (R2' F R F' R)
U2 R' U' (R2 U R' F' R U R' U' R' F R2 U' R') (U' R' U R)"
(↑R' U R U2') (r' R' F R F' r)
(↑ L U' L' U2) (l L F' L' F l')
U (R U R2' F R F') (R U' R' F' U F)
"U' (L' U' L2 F' L' F) (L' U L F U' F')
U (R' F R' F' R2) U' (R' U R f R' f')
 U2 (R' U' R U' R' U2) (R' D' R U' R' D R U R)"
U2 (↓r U' r U2') (R' F R U2') r2' F
(F U' R' U2' R U F') (R' U' R U R' U R)
(F' U L U2 L' U' F) (L U L' U' L U' L')
"U2 (R' U' R U' R' U R) (F U' R' U2' R U F')
(r U' r' U2) M' U' (R U r' U) F' U F"
"U2 (L U L' U L U' L') (F' U L U2 L' U' F)
(l' U l U2') M' U (L' U' l U') F U' F'"
"(R' U2' R U R' U R) (F U R U2' R' U R U R' F')
(R' U2' R U R' U R') (U' S' U2' S U' R) (F' r U R U' r' F)
(↑ l U L F2' L' F L F2' L2') (U L U2' l')"
"(L U2 L' U' L U' L') (F' U' L' U2 L U' L' U' L F)
(↑r' U' R' F2 R F' R' F2 R2) (U' R' U2 r)
 (F R U' R' U' R U2' R' U' F') (R' U' R U' R' U2' R)"
U (R U' R2' D' r U2 r' D R2) (U' R' U' R U' R')
U (R U R' U R U R2') (D' r U2 r' D R2 U R')
"(r' F R F') (r U' R D) (R' U' R D') R' U' R'
U' S (R' F' R f') U' F U2' f (R' F R f')
 U2 R' U2' R U' z U' R D' (R' U2' R' D) R U' z'"
"U2 (R U' R2' D') (r U2 r' D) R2 U R'
(L U' L2' D') (l U2' l' D) L2 U L'"
"(R' U R2 D) (r' U2 r D') R2' U' R
U2 (L' U L2 D) (l' U2' l D') L2' U' L"
"U' (↑R2' U' R U) F' (U2 R' U2' R) F U' R
F' U' L D (l' U2' l D') (L2' U L U') F
U (R U R' U') (R U R2' D') (R U' R' D) (R U2 R U' R')
 U (L' U' L) R U2' (L' U' L U') (R' U R U2' R')"
"U (↑ L2 U L' U') F (U2' L U2 L') F' U L'
F U R' D' (r U2 r' D) (R2 U' R' U) F'
U (R' U' R U) (R' U' R2 D) (R' U R D') (R' U2 R' U R)
 U R' U2 R L U' R' U L' U R U' R' U2 R"
"U2↑R' U F' (R' U2' R U2) F (U' R' U R2)
U2 (R U R' U2) (R' D' R U R' D) (R2 U' R' U R U' R')
 U' (R U2' R' U' R U) (L' U L U2') R' (L' U L)"
"U2↑ L U' F (L U2 L' U2') F' (U L U' L2')
(R' U' R U2) (R D R' U' R D') (R2' U R U' R' U R)
 U' R' U2' (R U R' U') (L U' L' U2') L R U' L'"
(f' U' F) (R' D' R U2) (R' D R U') (f R' F' R)
"↑R' UD' (R U2' R' D) (R' U' R U2) R' U' R2
(R U' R' U) (R U R' U') (R U R' U) (R' D' R U R' D R)"
"↑ L U'D (L' U2 L D') (L U L' U2') L U L2'
 U2 R U'D (R' U2 R D')·(R U R' U2') R U R2'
U' S (R U' R' U') (F' U2 F) (r' F R F') M' S'"
"U' x'· (R U2 R D2) (R' U2 R D2) R2' x
 (R' U2' R U') R' U' R y (R U R' U2') R U R'"
"U' x· (R' U2 R' D2) (R U2 R' D2) R2 x'
 U2 (R U2' R' U) R U R' y' (R' U' R U2') R' U' R"
"U' (↑R2' F' R U) (S' R U' R' f) (R B U B')
(↑R' U2 R' D' R U2 R' D) (R' U R' U R U2' R')
U2 (R U2' R' U' R U' R') (F U R U2' R' U R U R' F')"
"U (↑ L2 F L' U') (S L' U L f') (L' B' U' B)
(↑ L U2' L D L' U2' L D') (L U' L U' L' U2 L)
U2 (L' U2 L U L' U L) (F' U' L' U2 L U' L' U' L F)
 U2 (R U2' R D R' U2' R D') (R U' R U' R' U2' R)"
"U2 (R U2' R' U' R U' R2') (F' r U R U' r' F)
 U2 L' (R U R U') L U (R' U R' U') R U' R'"
"U2 (L' U2 L U L' U L2) (F l' U' L' U l F')
 L (R' U' R' U) L' U' (R U' R U) R' U R"
"U2 L' F' (L U' L' U2) (L U' L' U') F L
 U (R' U' R' D' R U R' D R) (U' R U' R' U2 R)"
U2 R F (R' U R U2') (R' U R U) F' R'
U (R' U' R U') (F U' R' U R U F') (R' U R)
"U' (L U L' U) (F' U L U' L' U' F) (L U' L')
 U R U R' L' U2 (R U' R' U2) L (U R U' R')"
"(F' U' F U) (R' F R2 U R' U') (R' F' R2 U R')
 U (R U R' U2') R d' (R U' R' U') (R U2' R' U2') F'"
U2 (F R U R' U') (R U' R' U' R U R' F')
U' (r U R' U') (r' F R F')
"(↓R U R D) (R' U M U2) r D' R2'
U2 (↑ L U L D) (L' U M' U2') l D' L2'
(R2 U' S' U2' S U' R2) U' (r U R' U' r' F R F')
 U2 (R' U' R UD') (R U' R U) (R U' R2' D)"
"(L' U' L U) (L U F' L' f) (L U' L' S')
 (R U R D) (R' U' R U'D') (R' U' R U) (R U R U' R)"
"U' (L' U' L U) (L F L' U2' L' U2 L F')
 U' (R U2' R' U2 R' F R) (U R U' R' F')"
U' F' U' (L' U2 L U') (L' U' L F)
"U' (R2 U' S' U2' S U' R2) (r U R' U' r' F R F')
U2 S' (L' U L2 U') (B U L2' U' B' L) S
U' (L U2 L2' U' L2 U' L') (F L' U2 L U2' L F' L')
U' (r U R' U' r' F R F') (R2 U' S' U2' S U' R2)"
(L U2 L') (F' U L U' L' U' F) (L U' L')
"U' (R U S' R' U') (R S R2' F R F')
U' (R U R' U' R U' R') (L U' R U R' L')"
U2 M (F R' F' r) U (R U R' U' R U' R')
 U' (M2' U M2' U2 M2' U M)(R U R' U' r' F R F')
M U' (r U R' U' R' F R F') M U M'
"(F U' f' U2') (L' U2 L U2') S
 U2 f R' F' U2 (R' U2' R U2) S'
U (L U2 L' U') (F' U L U L' U' F) (L U2 L')
U' (↓R U' R' U') (R U R D) (R' U2 R D') (R' U' R')"
"U2 (↑R' U' R' D') (R U' M' U2) r' D R2
(L2' U S U2 S' U L2') U (l' U' L U l F' L' F)
 (R U R' U'D) (R' U R' U') (R' U R2 u')"
U (R' F' r U) (R U' r' F)
(R U R' U') (R' U' F R f') (R' U R S)
U (R U R' U') (R' F' R U2 R U2' R' F)
"U (L2' U S U2 S' U L2') (l' U' L U l F' L' F)
U2 S (R U' R2' U) (B' U' R2 U B R') S'
U (R' U2' R2 U R2' U R) (F' R U2' R' U2 R' F R)"
U F U (R U2' R' U) (R U R' F')
(R' U2' R) (F U' R' U R U F') (R' U R)
"U (L' U' S L U) (L' S' L2 F' L' F)
(R U R' U') (R U' R' U') (F R U R' U' R' F' R)
U (L' U' L U L' U L) (R' U L' U' L R)"
"U2 (M F' r U R') U' (L' U' L U L' U L)
 U' (F U R' U' R F') (R' U' R U) R' U R"
U (M2' U M2' U2 M2' U M2')(R' F' r U R U' r' F)
"(F' U f U2) (R U2' R' U2) S'
(F' U F U2') (S' R U2' R' S)
U' (R' U2' R U) (F U' R' U' R U F') (R' U2' R)"
"M U (l' U' L U L F' L' F) M U' M'
 U2 M' U (r' U' R U R f' U' f) M' U' M"
"U' (R U R' U R U2' R') (L' U' L U' L' U2 L)
U (L' U' L U' L' U2 L) (R U R' U R U2' R')
U2 (F' R F R2' D' R) U' (R' D R2 F' R' F)"
"U (L' U' L U' L' U2 L) U (L' U2 L U L' U L)
 U' (R' U' R U' R' U2 R) U (R' U2' R U R' U R)
(L U' L' U2) L F' U2 (F U F' U) F L'"
"U' (R U R' U R U2' R') U' (R U2' R' U' R U' R')
(R' U R U2') R' F U2' (F' U' F U') F' R"
(R U2' R' U' R U' R') U (R U R' U R U2' R')
(L' U2 L U L' U L) U' (L' U' L U' L' U2 L)
"U' (R U R' U) (R U' R' U) (R' U' R2 U' R2' U2' R)
U (R' F' U' F U' R) U (R2' F R F' U R)"
"U (L' U' L U') (L' U L U') (L U L2' U L2 U2 L')
 U' (R' U' R U') (R' U R U') (R U R2' U R2 U2' R')
U' (L F U F' U L') U' (L2 F' L' F U' L')"
(R U2' R' U' R U' R2') (U2' R U R' U R)
"(L' U2 L U L' U L2) (U2 L' U' L U' L')
 U2 (R' U2' R U R' U R2) (U2' R' U' R U' R')"
U2 x' (·D R U' R' D') (R2 D2 R' U R D2 R2') x
"(L' U L2 F' L' F) (L' U B' U B U L)
 U' R' U' R2 U R2' U R2 U2' R' (U R' U R)"
"(R U' R2' F R F') (R U' B U' B' U' R')
 U' R U R2' U' R2 U' R2' U2' R (U' R U' R')"
(↓R U2 R D) (r' U2 r D') R2'
(↓R U2 R D) (R' U2 R D') R2'
"U (L' U R U' L U R2') (U2' R U R' U R)
U' f (R U R2' U')·S' (R' F' U F R F')"
"U' (F' L' U' L U2) (L F' L' f L' U' L FS')
U2 (↑ L U' L' U L U') F (L' U2' L U2) L F' L2'"
"(R u R' U R U' R u' R2') (U' F' U' F R)
U' (↑ L2 F L' F) M' U (L' U L U') l F2' L2'"
U (R U2' R2' D') (R U' R' D) R2 U' R'
"U' (R' U2' R U R' U xM) (U R U' L U R')
S (R U R' U' F' U2 F U R U R') S'
U' (R' U2' R U R' U R) (L' U R U' L U R')"
"U' (↓F2 U' F) (R2 u R' U) (R U' R u' R2) F
U2 (L2' U L U) (L2 U' L' U'D L' U2 L D' L2')
U R U R2' D' r U2 r' D R2 U' R' U' R U2' R'
(↑R2' U R U) (R2 U' R' U'D R' U2' R D' R2)
(R' U F U' F' U2' R) (F R' U R U2 F')"
"(F l' U' L2) (D' L' U' L D L' U2) l F' L'
 (R' U2' R F) (U R' U' R) F' U2 (R' U' R U') R' U R"
"R D2 (r' U' r D2) (R2' F' R U2') R' F R
 F' U2 F (R' U2' R U) F' (R' U R U2) F"
"F' R' U'D (R U' R' UD') R F (U' R' U2' R)
U S (R' U' F R' F' R2) U·F R F' U2 S'"
"U (M F R' F' r) U (R U R' U')2 R U' R'
(↓ L2' U L U'D) (L' U' L U2'D') (L U' L2' U' L2)"
"F (R U R2' F R F' R U' R') F'
 U' F (R U R' U') (R U' R' U2) (R U2' R' U') F'"
"U' (R U2' R2' U' R' U R2) (D' R U' R' U'D R')
 R' U'D (R' U' R D') (R2 U R' U') R2 U2' R"
"r U2' (R2' F R F' R) U2' r'
 U2 (R' U' R U') F U' (R' U' R U) F'"
"U l' U2 (L2 F' L' F L') U2 l
 U' z U (R U' R F') (R U R U') R' F z'"
"U (M' U l' U2) (L F' L' U2) l2 F' L'
 (R U2' R' U') F' (R U R' U R U2' R') (F R U' R')"
(M' U' r U2') (R' F R U2') r2' F R
"U' (R U2' R' U') (L' U2 l F) (M' U L' U L)
= U' (R U2' R' U') L' U2 R U R' (L U L' U L)
(F R U R'M') (S R' F R f') (R U' r' F')
(R U' R' U) (R U' R' U') (R U R' U2) (R' D' R U R' D R)"
"U2 (L' U2 L U) (R U2' r' F') (M' U' R U' R')
U (F' L' U' LM') (S' L F' L' f) (L' U l F)
 (R' U2 R U) L U2 R' U' R (L' U' L U') L'
U' (R' D' R U' R' D R) U2 (R U' R' U) (R U R' U' R U R')"
"U2 l' U' (L2 D L' U2' L D' L') U' (l F' L' F)
 U2 (F R' F' r) U' (R' D' R U2 R' D R2 U') r'
U (F' L' U' L U F) (l' U' l U' L' U M' U l)
(R U2' R2' F R F2') (L' B' U2 B L F)"
"U' r U (R2' D' R U2 R' D R) U (r' F R F')
=U' (r U R' U') (U R' D' R U2 R' D R U) (r' F R F')
(F R U R' U' F') (r U r' U R U' M' U' r')
U (L' U2 L2 F' L' F2) (R B U2' B' R' F')"
"U' (r U2' r'M) (F R' F' r2 U2' r')
=U' (L F2' L2') (R U R' U') (L2 F2' L')
U2 (R' F2 MR) (F' r U R2' F2 R)
=U2 (R' F2 R2) (L' U' L U) (R2' F2 R)"
"(r U2' r2' F R F') (M'r U2' r')
=(L F2 L2') (U R U' R') (L2 F2 L')
U (R' F2 R2 U' r' F) (M'R' F2 R)
=U (R' F2 R2) (U' L' U L) (R2' F2 R)"
U F' (r U R' U') r' F R
U2↑R2' D' (r U2 M U) (R' D R U R)
"S' L F' (U' L2' U) F (U' L2 U) L' S
U (F' L F l' U' L' U l) (L2 U' L2' S' L2 S U L2')
U' (R' F' R U2 R U2' R' F) (R' U' R2 U' R2' U2' R)
 U2 (R' U R U2) R' z U' R D (R U R U') R U z"
(R' U' R) (F U' R' U' R U F') (R' U2' R)
U2 F (R U' R' U') (R U2' R' U') F'
"U (F' L' U' L U) (L F L' U2' L' U2 L)
 U F' (R U2' R' U2 R' F R) (U R U' R')"
"(S' R' U' R) (f R' F' U R) (U R U' R')
U F U (R U2 R' U) R2 D (R' U R D') R2' F'"
"U (F' L F L2' S L) (U' L' S' U L)
 L' (R' U R U') L (R' U' R U') R' U R"
"U2 (L' U' L U') (L' U L U) (l F' L' F M')
 (L' U' L U') (L' U L U) (L F' L' F)
 (R' U' R U') (R' U R F) (R' U R U') F'"
U (F' r U R' U' r' F r)(M' U M2' U2 M2' U M2')
"U' S U2 (R U2' R' U2) (f' U' F)
U (S' R U2' R' S) (U2' F' U' F)"
M U M' (F' L F L') (U' L' U l) U' M'
U' (↑R' U2 R' D') (r U2 r' D) R2
U' (↑R' U2 R' D') (R U2 R' D) R2
"(R U' L' U R' U' L2) (U2 L' U' L U' L')
U2 f' (L' U' L2 U)·S (L F U' F' L' F)"
"U2 (F R U R' U2') (R' F R f' R U R' F'S)
U' (↑R' U R U' R' U) F' (R U2' R' U2) R' F R2"
"U (L' u' L U' L' U L' u L2) (U F U F' L')
U2 (↑R2' F' R F') M' U' (R U' R' U) r' F2 R2"
U2 (R' U2' R2 D) (R' U R D') R2' U R
"U2 (L U2 L' U' L U' xM) (U' L' U R' U' L)
U S' (L' U' L U F U2' F' U' L' U' L) S"
"U2 (↓ F2' U F') (L2' u' L U') (L' U L' u L2') F'
U' (R2 U' R' U') (R2' U R UD' R U2' R' D R2)
U (↑ L2 U' L' U') (L2' U L UD' L U2 L' D L2')"
U (F' r U R2') (D R U R' D' R U2') r' F R
"U' R' D2 (r U r' D2) (R2 B R' U2') R B' R'
 R U2' R' (F U2' F' U') R (F U' F' U2') R'"
"U F L UD' (L' U L U'D) L' F' (U L U2 L')
S' (L U F' L F L2') U'·F' L' F U2' S"
"(M F' L F l') U' (L' U' L U)2 L' U L
U (↓R2 U' R' UD') (R U R' U2D) (R' U R2 U R2')"
"(F R' F' r) (U R U' r')
= U' x' (R U' R' D) (R U R' u') z'"
U↓R2 D (r' U2 M' U') (R D' R' U' R')
"U S R' F (U R2 U') F' (U R2' U') R S'
(F R' F' r U R U' r') (R2' U R2 S R2' S' U' R2)
U2 (L F L' U2' L' U2 L F') (L U L2' U L2 U2 L')
 U' L U' (R U R') L' U2 (R U' R' U') R U' R'"
"U (L U L') (F' U L U L' U' F) (L U2 L')
 U2 (R' U2 R U'D') U' (R U' R U) (R U' R2' D)"
U' F' (L' U L U) (L' U2 L U) F
(F R U R' U') (R' F' R U2 R U2' R')
"U (S L U L') (f' L F U' L') (U' L' U L)
 U' (S' R U R') (F' U f U') (R' U' R' U R)"
"(F R' F' R2 S' R') (U R S U' R')
 U' L (R U' R' U) L' (R U R' U R U' R')"
"U' (R U R' U) (R U' R' U') (r' F R F' M')
 (R U R' U) (R U' R' U') (R' F R F')"
(F R' F' r U R U' R')(M' U M2' U2 M2' U M2')
"U2 S' U2' (L' U2 L U2') (f U F')
U2 (S' R' U2' R S) (U2' f R f')"
U M U' M' (F R' F' R U R U' r') U M'
"U2 (R U R' U') (r' F R F') (R' F R F') (r U R')
U (R U' L' U R' U' L) (F R' F' r U R U' r') (wyh)
U' (F' R F R2' D' R) U2 (R' D R2 F' R' F)
 U2 (R U2' R' U2) (R' U' R U) (R U' R' U2) R' U2' R"
(R U2' R' U' R U' R') U (R' U2' R U R' U R)
U (L' U2 L U L' U L) U' (L U2 L' U' L U' L')
"(R U R' U R U2' M'x') (U2 L' U' L U' L')
 (R U R' U R U2' R') U2 (R U2' R' U' R U' R')"
U (L' U' L U' L' U2 L) U' (L U L' U L U2 L')
(R U R' U R U2' R') U (R' U' R U' R' U2' R)
"↑ f' (L U' L U L' D) (L' U' L E) r
U2↓b' (R U' R U R' D) (R' U' R E) l
U (L2 U L' U') (L' U L U) (L' U L U') (L U' L2')
U2 (R U2' R' U' R U' R2') (U2' R U R' U' R U R' U R)
U' R2 U (R' U' R' U) (R U R' U) (R U' R U') R2'"
"U2↑r' E' (L' U L D') (L U' L' U) L' f
↓l' E' (R' U R D') (R U' R' U) R' F z'
U2 (R2 U R' U) (R' U' R U') (R' U' R U) (R U' R2')"
"U↑f (R' U R' U' R D') (R U R' E') l'
(↑R2' U' R U) (R U' R' U') (R U' R' U) (R' U R2)"
"U'↑ l E (R U' R' D) (R' U R U') R f'
U (↑R2' U' R U') (R U R' U) (R U R' U') R' U R2"
U2 (R U R' U) (R U' R' U)2 (R U2' R')
"(R U2' R' U' R U' M'x') (U L' U L U2 L')
 (R U2' R' U' R U' R') U2 (R U R' U R U2' R')"
"U2 (f' L' U' L U S) (L' U L U' L' U' L F)
 U2 L (R' U' R U') (R' U R U2) L' U R' U2' R
U' (F' r U R' U' r' F R2) (U2' R' U' R U' R')"
"U2 (f R U R' U' S') (R U' R' U R U R' F')
U (F l' U' L U l F' L2') (U2 L U L' U L)"
"U (F R U R' U') (R' F' U2' R U R' U R2 U2' R')
 (F R U' R' U' R U2' R' U' F') (R U2' R' U' R U' R')"
"U2 R F (R2' U' R2 U' R2' U2' R2 U') F' R'
 U R' D (R' U2' R U2') (R' U R U) (R' U' R D') R"
"U2 L' F' (L2 U L2' U L2 U2 L2' U) F L
 U2 F U' (R U2' R' U2) (R U' R' U') (R U R' U) F'"
"U2 (↓ l' U2' L' D') (L U L' UD) (l F' L F)
 U' (R U2' R' U) L' U2' (R U2' R' U2') L R U' R'"
"U2 (↓r U2 R D) (R' U' R U'D') (r' F R' F')
 U (R U2' R' U') (R U R' U')2 R U2' L' U R' U' L"
(F R U' R' U R U2' R' U') (R U R' U' F')
"U' (L' U2 L2 F') U (L2' U L2 U') F U' L'
 f U (R U' R' U) R U' F' (R U R' U') R' S'"
U (R U2' R2' F) U' (R2 U' R2' U) F' U R
"f (R2' S' U' R2 U') (R2' U R2 F')
 U R U2' R' L' U2' (R U' R' U2') L (U' R U' R')
U' F' (R U2' R' U2) (R' F R U) (R U R' U') R U' R'"
"f' (L2 S U L2' U) (L2 U' L2' F)
 U (R' U2 R U2') (R2' F' R U) (R U' R' F) U R"
F (R' F R F') (R U2' R') (F R' F' R) F'
"(L F' L F L2') U' (L U L' U f' L f)
(f R f' U R' U R U') (R2' F R F' R)"
(R' F R' F' R2) U (R' U' R U' f R' f')
"U F (U R U' R')3 F'
 U F (R U R' U')3 F'"
"U' (R U' R2' U') F2 U' (R2 U R2' U) F2 R2 U R'
 U (R U R' U R U2' R') (L' U2 R U' R' U2' L R U' R')"
"U (L' U L2 U) F2' U (L2' U' L2 U') F2' L2' U' L
 U2 (R' U' R U' R' U2' R) U (R' U' R U' F U' R' U' R U F')
U' (R U' R2' F2) U' (R2 U' R2 U) F2 U R2 U R'"
"(l' U2 L2 F' L' F L' U2 l2x) (U R' U R U2' R')
 (R U2' R' U' R U' R') (L' U2 R U' R' U2' L R U' R')"
"(r U2' R2' F R F' R U2' r2'x) (U' L U' L' U2 L)
 (R' U2' R U R' U R) U (R' U' R U' F U' R' U' R U F')"
"U' F l F' (L2' U2 L U L' U L) U (r U R' F')
U' F' r' F (R2 U2' R' U' R U' R') U' (l' U' L F)"
"U (L' U' L2 F' L' F) (R' F R U' R' F' R)
 U2 (R U R' U R U2' R) (D' R U' R' D R U R)"
U (R U R2' F R F') (L F' L' U L F L')
"U x· (R D' R' U) R2' D (R U R U2') r' U2 L
 (R U R' U R' U') (R2 U' R2' U') z U R' D R U' z'
(L' U' L U' L' U' R U' L U R) (U' S' U2' S U' R2)"
"U x·(L' D L U') L2 D' (L' U' L' U2) l U2' R'
 U2 x' U' R U R' x U2' (R' U2' R U') (r U2' R' U' R U' r')
U2 (R U R' U R U L' U R' U' L') (U S U2 S' U L2')"
"U S' (R f' U' F) U2' (↑R2' f R F' R) S
 U' (R U2' R2' U') R' D (R' U' R D') R U2' R
(↑R2' D' R U2 R' D) (R' U R2' U R2 U2' R')"
"U S (L' f U F') U2 (↑ L2 f' L' F L') S'
 R2 D (R' U2 R D') (R U' R2' U') R2 U2' R
(↓R2 D R' U2 R D') (R U' R2 U' R2' U2' R)"
"(L' U' L U' L' U') (R U' L U R')
 U2 (R' U' R U' R' U') (L U' R U L')"
U2 (R U R' U R U) (L' U R' U' L)
"(R U2' F R' F') U2 FS' U' (f R F2' R')
 U' (R U R' U') L' U2' R U2' R' z (R U R' U') R2 U z'"
"U' (↑r' F R' F' r U2 R U') (R' U' R U R' U' R)
= U' (L' U R' U' L) U2 (R U' R' U') (R U R' U' R)"
"U' (↑ l F' L F l' U2' L' U) (L U L' U' L U L')
= U (L U' R U L') U2 (R' U R U) (R' U' R U R')"
U (R' U2' R U R' U R) U (R U R' U R U2' R')
U (R U2' R' U' R U' R') U' (R' U' R U' R' U2' R)
U' (R' U2' R U) (R' U' R U R' U R)
"U' (R U2' R' U') (R U R' U' R U' R')
U (L U2 L' U') (L U L' U' L U' L')"
(R U R' U) (R U' R' U R U2' R')
"U2 (L' U' L U') (L' U L U') L' U2 L
 (R' U' R U') (R' U R U' R' U2 R)"
M'(r U R' U R U' R' U R U2' r')M (U M' U2 M)
"U (R' F R U) M'R' (F R U' R' F') MR
 (R U R' U R U2' R') U' (R' U2' R U R' U R)"
"U' (L F' L' U' L F L') (F R' F' R2 U' R')
=U' (r U' r' U' r U r') (F R' F' R2 U' R')"
U (R' F R U R' F' R) (F' L F L2' U L)
"F (R U' r' U') (L' U' L U' L' U2 L2x) U R' F'
F' (L' U l U) (R U R' U R U2' R2') F' r F
 U2 (F U R U2' R' U R U R' F') (R U2' R' U' R U' R')"
"U S (L F' L f L2') (U2' F U' f') L S'
 U' (R U R' U) R2 D (R' U' R D') (R2' U R U2 R')"
"U' S' (R' F R' f' R2) (U2 F' U f) R' S
 U' (R' U' R U') R2' D' (R U R' D) (R2 U' R' U2 R)"
U' (R U' L' U R' U) (L U L' U L)
U (L' U R U' L U') (R' U' R U' R')
"U (↓R U2' l' U2) (L U L D) (L2' U L' D' L) x'
 U' (L U2' r' U2) (R U R D) (R2' U R' D' R) x"
U' (↓ L' U2 r U2') (R' U' R' D') (R2 U' R D R') x'
"U' (R F2' R' f') U↓SF' U2' (F R F' U2 R')
 U' z U' R2 U R U' R' z' (R U2' R' U2') L (U R U' R')
U (↓R U2 R' U') R U (L' U2 L U2) R' (U' L' U L)"
"U (↑R' U R U' R' U R U) (R' U2' r' F R F' r)
= U (R' U R U' R' U R U) (R' U2' L' U R U' L)"
"U' (↑ L U' L' U L U' L' U') (L U2 l F' L' F l')
 U (R U' R' U) (R U' R' U') (R U2' L U' R' U L')"
"U' (R F U' R2') U' (R U' R' U2') (R2 U F' R')
U' F (R2' U' R U') (R U' R' U2) (R' U R2 F')"
"U (L' F' U L2) U (L' U L U2) (L2' U' F L)
 U F (R2 U' R U2) (R U R' U) (R' U R2 F')
U (R F U' R2') U2' (R U R' U) (R2 U F' R')"
"U2 (R U R' U) (r' F R F') (r U' R' U R U2' R')
 (R U2' R' U') R U L' (U R' U') L (U' R U' R')"
U' F U (R' U' R2 U' R2' U2' R U2) (R U R' F')
"U' (R' F' U' F U' R) U (S' R' U R S)
 U' r' U' (R U' R' U)2 (R' F R F') U r"
"U (L F U F' U L') U' (S L U' L' S')
 (R U2 R' U') F' (R U2 R' U') (R U' R' F) R U' R'
U (S' R' U' R S) U' (R' U F' U F R)"
"(F' R U F2') (R' U R U') (F2' U' R' F)
 U' (R' U R U2') L (U' R' U R) L' (U2' R' U' R)"
"(F L' U' F2) (L U' L' U) (F2 U L F')
 U' (R U' R' U2') L' (U R U' R') L (U2' R U R')"
"U2 (F' R U F2') (U R' U' R) (F2' U' R' F)
 U (R' U R U2') L (R' U' R U) L' (U2 R' U' R)"
"U2 (F L' U' F2) (U' L U L') (F2 U L F')
 U (R U' R' U2') L' (R U R' U') L (U2' R U R')"
"U2 R D (R' U R D') (R2' U2' R U') (R' U R U R' U R)
 U (↑R' U' R U') (R' U' R U) (R' U' R' D') (R U' R' D) R2"
R' D' (R U' R' D) (R2 U2' R' U) (R U' R' U' R U' R')
"U2 (F R U' R' U' R U R' S) (U R U' R' f')
U2 (L' U' L U' L' U2 L2) (F l' U' L' U l F')"
"U2 (F' L' U L U L' U' L S') (U' L' U L f)
= U' (R' U2' R U') L U2' (R' U' R U) R' U R L'
U2 (R U R' U R U2' R2') (F' r U R U' r' F)"
"(R U2' R2' U') (R U' R' U2' F R) (U R U' R' F')
U2 (R' D' F2 UD) (R D' R' F2) (R2 U' R' U'D R')"
"U (↓F R F' r) (UD R' U R D') R' U2' r'
= (R' U' R) L U2 (R' U2 R U2) L' (U R' U2 R)"
"U' (↓F' L' F l') (U'D' L U' L' D) L U2 l
= R' U L U R' D' (R U2 R' D) R2 U L'"
"R' B' U' (R2 U2' R2' U' R2 U' R2') B R
 U2 F U' (R U' R' U) (R U R' U2) (R U2' R' U) F'"
"L B U (L2' U2 L2 U L2' U L2) B' L'
 U R' D (R' U R U') (R' U' R U2') (R' U2' R D') R"
"↓F (R2 U' R2' U) (R2 U S R2') f'
U2 (R U R' U) (R U' R' U') R' F' (R U2 R U2') R' F"
"↓ F' (L2' U L2 U') (L2' U' S' L2) f
 U' R' U' F' (R U R' U') (R' F R2 U2' R' U2 R)"
(F U R U' R') (U R U2' R' U' R U R' F')
U2 (R' U' F U') (R2 U R2' U) (F' R2 U2' R')
"U2 (L U F' U) (L2' U' L2 U') (F L2' U2 L)
 U' z (U' R' U') L' (U R U') L U' (R U' R U) R2 U' z'"
"U (R U2' R') (F R' F r) U (r' F2 R F')
 U' L' (U R' U' R) L U2' (R' U2' R U') R' U2' R"
"U2 (F U R U' R' S) (R' D' R U R' D R2 U' R' f')
 U2 F' U' F (R U R' F) (R' F' R2 U R' U') R U' R'"
U2 f R' (U2'↓↓R' F' R2' F R U2') F' R S'
"U' S' L F' (U2↓↓ L F L2 F' L' U2) L' f
 U' R' F (R U R' U') R' F' (R2 U' R' U) (R U' R' U2 R)"
"U2 (R U R' U F2 R U2' R') (U2' R' F2 R)
 U2 (L U' R' U L' U') (R U' R' U2') (R U R' U R)"
"(R U' L' U R' U' L2) (U L' U L U2 L')
 U2 (L U' R' U L' U') (R2 U R' U R U2' R')"
U2 (R' U2' R U R' U R2) (U' L' U R' U' L)
"U (L F2' L' U2) (L' U2' L F2' U L' U L)
 U' (R U R' U R U2' R') U' (R U' L' U R' U' L)"
U' (R U R' U' R' F R2 U R' U') (R U R' U' F')
"U (L F2' L' F) (R' F R F') M' U' (l F2' L' F)
 U' (R' U' R U' R' U2' R) (F U R' U' R F' U' R' U2' R)"
"(M F' r U R') U2' (L' U L U' L' U2 L)
 U F (U R' U' R) F' U' (R' U R U') R' U2' R"
"U' (R U2' R' U') (R U R' U2') (r' F R F' M')
= U' (R U2' R' U') (R U R' U2') L' (U R U' R') L"
"U' (L' U2 L) (F' L F' l') U' (l F2' L' F)
 U' L (U' R U R') L' U2' (R U2' R' U) R U2' R'"
"U2 (F' U' L' U L S') (L D L' U' L D' L2' U L f)
 U2 (R U R' U) (R U' R2' F R F') (R U' R') F' U F
U' (f R U R2' D' R U' R' D R) (S' R U R' U' F')"
"U2 f' L (U2↓↓ L F L2 F' L' U2) F L' S
 U' L' (R U2' R2' U') (R2 U' R' U') L (U R' U2' R)"
"U S R' F (U2'↓↓R' F' R2' F R U2') R f'
 U2 (R U2' R' U) L (U' R' U' R2) (U' R2 U2' R) L'"
"U2 (L' U' L U' F2' L' U2 L) (U2 L F2' L')
 U2 (R' U L U' R U z U' R' z') (R U2' R' U' R U' R')"
(L' U R U' L U R2') (U' R U' R' U2' R)
"U2 (L U2 L' U' L U' L2') (U R U' L U R')
 (R U2' R' U' R U') (R2' U L U' R U L')"
"U' (R' F2 R U2') (R U2 R' F2 U' R U' R')
 U' (R' U' R U' R' U2' R) U' (L' U R U' L U R')"
"U (L' U' L U L F' L2' U' L U) (L' U' L U F)
 (F U R U' R') (U R U' R2' F' R U R U' R')"
"U' (R' F2 R F') (L F' L' F) M' U (r' F2 R F')
U' (R' U' R U) R U' F U' (R' U' R U) F' (U2' R2 U2' R)"
"(M F R' F' r) U2 (R U' R' U R U2' R')
 L' (R U R' U') L U2' (R U' R' U) R U2' R'"
"U (L' U2 L U) (L' U' L U2) (l F' L' F M')
 U' (R' U2' R U) (R' U' R U) F (R' U R U') F'"
"(L' U' L U' L' U2 L2) (U2 L' U' L U' L')
U (F U R U' R' F2') (L' U' L U F)
 U2 (R' U' R U' R' U2' R2) (U2' R' U' R U' R')"
"(R U R' U R U2' R2') (U2' R U R' U R)
U' (F' U' L' U L F2) (R U R' U' F')"
"U (F U R U' R' S) (U R U' R' f')
 U' (R' U' R U' R' U2' R) U (R' U' R U' R' U2' R)"
"U' (F' U' L' U L S') (U' L' U L f)
(R U2' R' U' R U' R') U (R U2' R' U' R U' R')"
"U' (R' U2' R2 U R2' U' R2 U2' R') (S R2' S')
 U (R U' R' U2) (R U R' U2')2 R U2' R'
U (↑R' U R U') (R2' U2' R U) (R' U R2 U') R' U R"
"U' (R U2' R2' U' R2 U R2' U2' R) (S R2' S')
 U (R' U R U2') (R' U' R U2')2 R' U2 R
U (R U' R' U) (R2 U2' R' U') (R U' R2' U) R U' R'"
"U' (S R2' S')·(R' U2' R2 U' R2' U R2 U2' R')
 (↑R' U2 R U2') (R' U R U2')2 R' U' R"
"U' (S R2' S')·(R U2' R2' U R2 U' R2' U2' R)
 U2 (R U2' R' U2) (R U' R' U2)2 R U R'"
"U' R' U2' R2 U R2' U R2 U2' R'
U L' U2 L2 U L2' U L2 U2 L'"
"U' R U2' R2' U' R2 U' R2' U2' R
U L U2 L2' U' L2 U' L2' U2 L"
"U' S (R' U2'↓↓R2 U) (S R2' S') (U' R2 U2 R) S'
 U' (R U R' U') (R' U' R U) (R U R' U') (R' U R U') R U' R'
U' F (R U R' U')2 F' (R U R' U' M' U R U' r')"
"U' (R U2' R2' U') (S R2 S') (U' R2' U2' R)
 U' (R U2' R' U' R U' R') U' (R U2' R' U' R U' R')
(R U R' U R U2' R') U (R U R' U R U2' R')"
U2 S' U2' (L' U2 L U2' L F' L' f)
"(S' L' U' L U L F' L' S) (L' U' L U F)
 U' (R' U' R U) (R2 U' R' U') R UD' (R U R' D) R'"
"U (↓R U2 R D) (R' U' R D') (R2' U R U2 R')
U S' U' F (U R U2' R') S (U' R U R' F')
U2 (R U R' U R2) (D R' U2 R D' R2')
"U2' (L' U L U2') (L' U L2 D) (L' U L D') L'
 U' (↓R U R' U) R2 D (R' U' R D') R' U' R'"
(L' U2 L U2') (l F' L' F M')
U2 (R U R' U R2) (D r' U2 r D' R2')
"U (L2' D' L U' L' D L2) U (l F' L' F M')
U R' F (R U R' U') R' F' D' (R U R' D) R2"
U (L' U2 L U) (F l' U' L U l F' L2') U L
"U2 (L U L' U') (L F' L' U' L U)·L F L2'
(R U R2' F') (R U2 R U2') (R' F R U' R')"
"(L' U2 L U2' l F' L' F) (M U M2' U2 M2' U M2)
(↓R U2 R D) (R' U2 R D') (R' U R' U R U2 R')"
"U (L' U' L U') L F' U (L2' U L2 U') F U' L'
 U' (R' U2 R' D) (R' U R D') (R U R U') R U' R'"
"U' (L' U2 L2 U L2' U L) (F' U L U L' U' F)
F U' (R' U R U) F' (R U R2' U) R2 U2' R'"
U' (R U' R2' U2' D') (R U R' UD) R2 U R'
"U' L2' D' (L U' L' UD) (l F' L F M')
U' R U' L' U (R' U' R U') L U R' (U' L' U L)"
"U2 (L' U2 l F' L F l') (U L' U L)
(R' U2' L U' R U L') (U R' U R)"
"U' (F' U L U' L' U' F) (L U' L' U L U2 L')
U' R U2' L' (U R' U' R) L U' (R' U R U2' R')"
(R' U2' R U R' U' R) (F U' R' U' R U F')
U2 (R U R' U) (r' F R F') (r U2' R')
"U' (f R' F' R) f' (R' D R U R' D' R U2') F
F (R U R' U) (R U2 R U2') (R2' U' R2 U' R2' F')"
"U' (F' L' U' L U) (L' U' L F' L F L' U F)
U F U (R' F R F') (R U' R' U) (R U' R' F')"
"(R' F R F') U (R U R' U2') (F R' F' R)
(R U R' F') (R U R' U R U2 R') (F R U' R')"
"U↓F' (R U R' D) (R U R' U'D') (R U' R' F)
U' R' U' F' U (L' U L U')2 F R"
"U' F (L' U' L U'D') (L' U L D) (L' U L F')
U R U2' L' (R' U2' R U2') R' U2' L (U' R U' R')"
U' (F R' U2' R F') (R' F U2' F' R)
"(L2' D' L U' L' D L) (U' L U L' U L)
U2 (R2' D' R U' R' D R) (U' R U R' U R)"
U' (R U R' U R U') (R D R' U' R D' R2')
U' (F R' U R U F') (R' U F U F' R)
"U↓R2 F2' (D r' U2 r D') F2' R' U2' R'
(R U R' U) (R' F R F') (R U' R') (F' U F) R U' R'"
"U (R U2' R2' F R F') (R' U' F' U F R2 U' R')
U2 (R U2 R' U') (R U R' U') R U R D R' U2 R D' R2'"
"(↑R' U2' R' B2') (D' r U2 r' D) B2' R2
D' (↓R2 U R' U) (R2' U' R U') R2 D R' U2 R
U2 (R U' R' U') (R U' R' U2) (R U R2' D') (R U2 R' D) R"
"U2↑R2' D' (r U2 M U R' D) (R U' R U) R' U R
U' (R U R' U R U' R D R' U' R D') (↑↑U' S' U2' S U' R2)
U (↑R' U' R F) U' (R' U R U) F' (U2' R' U2 R)
"U L' U2 B' L F L' B L F' (U L' U L)
U' R' U2 R' D' (R U R' D) (R U' R U) R' U R"
"U2 (R U R' U) F' R B R' F R B' U2' R'
U' (R U R' U) R' D' (R U R' D) (R U' R U2' R')"
"R B' R' S'F (R' D R) SF' R B U' R'
S U R' U' F R F' U R U' F R' F' R S' 
U R' U2 R U R2' D' (R U2 R' D) (R U R U') R' U' R"
R U' L' U R' U' L
"↑ L U2' (L F L' U') (L' U L F') U2 L'
U R U2 R' U2 R' F (R2 U R' U') (R U R' U') F'"
U'↑R' U2 F' (R U R' U') (R' F R U2' R)
"(R U' L' U R' U' L') (U S U2 S' U L2')
S U (↑R' U' R' U R2 U' R') (f' U F)
U R' U' (R' U R2 U2'D') (R U R' U'D) R'"
"(R2 D R' U2 R D' R' U') (R' U R U2 R')
(R U' L' U R' U' L') (U' L2' S' L2 S U L2')"
"U' (F U f') (L' U' L2 U) (L' U' L' U) S
U f R F' R' U' R2 U R' U' R' U S'
U' R' U'D (R' U R U2D') (R2 U R' U' R')"
"(R2 U' S' U2' S U' R') (U' L' U R' U' L)
 U↑R' U2' (R U R' U') R' D' (R U2 R' D) R2"
"(M'L F' L' F) (l' U' l U2') (M' U' M2')
↓R2 D (r' U2 r D') (R' U' R' U) R U2 R'
  R2' U (R U R' U') (R' U' R') L' (U R' U') L"
"U' (M2' U' M U2) (r U' r' F) (R' F' MR)
U (R' U2' R U) (R' U' R' D') (r U2 r' D) R2"
"(↑R2' D' F U'D) (F U F2) (R2 U R2' F R2)
U2 (R U R' F') (R U R' U) (R U' R' U') (R' F R2 U' R')"
"R2 S2' (R' U' L' U R' U' L') S2 L2
U (r U2' R' U') (R U R' U') (R U R' U2) (r' F R F')"
"U' (R' U F U2') (r U' r' U') (R U' R' F' R)
(R U' R' U) (R U' R' F) (R' F' R U') F' U F"
(f R' F' R U2 R U2' R') U2 S'
U (↑R' U2 R U) (R2' D' R U' R' D) (R U2 R)
(F U R U' R' S) (R' F' R U R U' R' S')
"(L2' D' L U2' L' D L2) (U L' U L)
U2 (R2' D' R U2 R' D R2) (U R' U R)"
"(L2' D' l U2' l' D L2) (U L' U L)
U2 (↑R2' D' r U2 r' D R2) (U R' U R)"
"U (R U R2') (F' r U R U' r' F) (U R U2' R')
U (R U R' U) (R' U' R' D') (R U R' D) R' U2 R'"
"U' (↑R' U' R' D') (R U' R' D) (R2 U R' U R)
U R' D' (R U R' D) (R2 U R' U2) R U R'"
"(M F R' F' r) (U2 R U2' R')
L' (R U R' U') L (U2 R U2' R')"
U' (M F R' F' r) U (R2 D R' U' R D' R2')
"U2 (L' U' L F) (L' U2 L U2') (L F' L2' U L)
(↑R2' F R U) (R U' R' F') (R U' R' U R)"
"(M2' U M2' U2 M2' U M') (F R' F' r U2' R U2 R')
(↑R' U2 R U) (R' U R' D') (R U2 R' D) R U2 R"
U' R' U' F U' (R2 U R2' U) F' (R U' R U' R')
"(R2 U' S' U2' S U' R') (U R' U R U2' R')
 U' R' U (R2 U R' U) (R U2' R U2') (R U R' U) R2
U2 L F2' (L' D' L D) F2' U (L2' U' L U L2')
U' (R' U2' R U R' U R') (U' S' U2' S U' R2)"
"U L' U2 L U L' U L
 U' R' U2' R U R' U R"
"R U R' U R U2' R'
U2 L U L' U L U2 L'"
"(R' F' U' F U R) (F U R U' R' F')
 U' (R' U' R U) (R U R' U') (R' U R U) R U' R'"
"(R U R2' U' R2 U' R2' U2' R2) U2 R'
(SF' L' f) U' (L2 f' L' F L') S'"
"(R U R' U R U2' R) (U' S' U2' S U' R2)
 U' (R U R' U') (R' U2' R U) (R U' R' U) R' U R"
"U2 (L2' U S U2 S' U L') (U L' U L U2 L')
(R' U2' R2 U2') (R2' U' R2 U') R2' U R
U S' (R' F R' f' R2) U' (f R' SF')"
"U' S' U2' (l' U2 L U L' U l) S
U S U2 (r' U2' R U R' U r) S'
 U2 (R' U' R U') (R U R' U) (R U2' R' U') R' U R"
"S (r U R' U R U2' r') U2 S'
 U' (R U R' U') R' U2' (R U R' U) (R U' R U' R')"
U' (↓R2 U' R2' U') (R U2 R U') (R' U' R U) R2'
"(L' U' L U') (L U L2' U L2 U2 L')
U2 R' U' R U' R U R2' U R2 U2' R'
U' (R' U2' R2 U R2' U R) (U' R U' R')"
"U (L2' U L U') (L' U' L U2') (L U' L2' U' L2)
 U'↑R2' U (R U' R' U') (R U2 R U') (R2' U' R2)"
U2 S U2 (R U2' R' U2 R' F R f')
"U (↑R' U2 R' D') (R U R' D) (R2 U' R' U2 R)
U' S U F' (U' L' U2 L) S' (U L' U' L F)
(S R U R' U' R' F R S') (R U R' U' F')
"U2 (L' U' L U' L2') (D' L U2' L' D L2)
(↑R' U' R U' R2') (D' R U2 R' D R2)"
U2 (R U' R' U2) (R U' R2' D') (R U' R' D) R
(R U2' R' U2) (r' F R F' M')
U' (R2 D R' U R D' R2') U' (r' F R F' M')
"U2 (L' U' L U' L2') (D' l U2' l' D L2)
(↑R' U' R U' R2') (D' r U2 r' D R2)"
U' (R U2' R' U') (F' r U R' U' r' F R2) U' R'
U2 (R' U' R U) (R' F R U R' U')·R' F' R2
"(R U2' R' U2 r' F R F') (M U M2' U2 M2' U M2')
U2 (↑R' U2 R' D') (R U2 R' D) (R U' R U' R' U2 R)"
U' (R U R' U) R' F U' (R2 U' R2' U) F' U R
U (R U2' R2' U' R2 U' R') (F U' R' U' R U F')
U' (R' U R2 U2' D) (R' U' R U'D') R2' U' R
U R2 D (R' U R U'D') (r' F R' F' M')
"U2 (R U2' r' F R' F' r) (U' R U' R')
= U2 (R U2' L' U R' U' L) (U' R U' R')"
U (F U' R' U R U F') (R' U R U' R' U2' R)
"(L U2 L' U' L U L') (F' U L U L' U' F)
U (R U2' R' U') (R U R') L' (U R U') L U2' R'"
"U2 (L' U' L U') (l F' L' F) (l' U2 L)
 (R' U' R U') (r x' U' R' U) z U' R2 D z'"
"U (f' L F L') f (L D' L' U' L D L' U2) F'
U2 F' U2 (R' D R U' R' D' R) (f R' F R f')
U2 (R U2' R' U') R U (L' U L U2') R' (U' L' U2 L)"
U (F R U R' U') (R U R' F R' F' R U' F')
"(R' F R F') U2 (R U' R' U') (F R' F' R)
U2 (R U R' F') (R U2' R' U' R U' R') (F R U' R')"
"U'↓ F (L' U' L D') (L' U' L UD) (L' U L F')
 U L U F U' (R U' R' U)2 F' L'"
U F' (R U R' UD) (R U' R' D') (R U' R' F)
(R' F U2' F' R) (F R' U2' R F')
(R2 D R' U R D' R') (U R' U' R U' R')
"U (L' U' L U' L' U) (L' D' L U L' D L2)
 U' (R' U' R U') (R' U R' D') (R U R' D) R2"
(R' F U' F' U' R) (F U' R' U' R F')
"U↑R2' B2' (D' r U2 r' D) B2' R U2' R
 U R' D' (R U2 R' D) (R2 U' R' U2) (R U R' U) R U R'"
"U' (L' U2 L2 F' L' F) (L U F U' F' L2' U L)
↑R' U2 F' (R U R' U') (R' F R2 U R' U R)"
"U' (↑R' U' R U') (R' U R' D') (R U' M' U2) r' D R2
U (L' U' L U' L' U L' D' L U L' D) (↑↑ U S U2 S' U L2')
"U2 (↓R U2' R F2') (D r' U2 r D') F2' R2
U2 (R U R' U') (R' F R U2) (F' U' F U') (R U R' U') F'"
"U' (L U L' F') U (L U' L' U') F (U2 L U2' L')
U' R U R2' F' U' F U R F R' F' R2 U2 R'"
"U R U B' R' S'F (R' D' R) SF' R B R'
U2 S R' F R F' U R' U' F R' F' U R U' S' 
(R' U' R U') (R U R' U') (R' U2' F R) U (R U' R' F')"
"U2 (L' U' L U') F L' B' L F' L' B U2 L
(R' U' R U') (R' U R' D') (R U' R' D) R U2 R"
"U' R U2' B R' F' R B' R' F (U' R U' R')
U' (R U2' R' U) R' D' (R U' R' D) (R U' R U' R')"
"(f' L F L' U2' L' U2 L) U2' S
 U (R U2' R2' D') (R U2 R' D) (R2 U' R' U) R U' R'"
U (↓R U2 R' U') (R2 D R' U R D') (R' U2 R')
(F' U' L' U L S') (L F L' U' L' U L S)
(R2 D R' U2 R D' R2') (U' R U' R')
(R2 D r' U2 r D' R2') (U' R U' R')
"U' (L' U' L2) (F l' U' L' U l F') (U' L' U2 L)
U (R' U' R U') (R U R D) (R' U' R D') R U2 R"
"(M F' L F l') (U2 L' U2' L)
 U (F U R' U' R F') (U' R' U2' R)"
U' (↓R U R D) (R' U R D') (R2' U' R U' R')
"U (M F' L F l') U' (L2' D' L U L' D L2)
U2 R2' D' (R U' R' D) F (R U R U') R' F' R"
U2 (R U R' F') (R U2' R' U2) (R' F R2 U' R')
"(M2' U M2' U2 M2' U M') (F' L F l' U2 L' U2' L)
U2 (↓R U2 R' U') (R U' R D) (R' U2 R D') R' U2' R'"
U L U F' U (L2' U' L2 U') F (L' U L' U L)
L' U R U' L U R'
↑R' U2 (R' F' R U) (R U' R' F) U2' R
"U↑ L U2' F (L' U' L U) (L F' L' U2 L')
F U (R U' R' U) (R U' R2' F') (R U2 R U2') R'"
"(L' U R U' L U R) (U' S' U2' S U' R2)
U2 S U' (↓R U R U' R2' U R) (F R' f')
U (R U R U') R2' U2D (R' U' R UD') R"
"U2 (↑R2' D' R U2 R' D R U) (R U' R' U2 R)
(L' U R U' L U R) (U R2 S R2' S' U' R2)"
"U (F' U' f) (R U R2' U') (R U R U') S'
U' R UD' (R U' R' U2D) R2' U' R U R"
"(L2' U S U2 S' U L) (U R U' L U R')
 U (↓R U2 R' U') (R U R D) (R' U2 R D') R2'"
"(M'R' F R F') (r U r' U2) (M' U M2')
U2↑R2' D' (r U2 r' D) (R U R U') R' U2' R"
"U (M2' U M U2) (R' F R F') (r U Mr')
U (R U2 R' U') (R U R D) (r' U2 r D') R2'"
"(↑ L2 D F' UD') (F' U' F2') (L2' U' L2 F' L2')
(R' U' R D') (R U' R' U) (R2 U R' U') R2 D"
"L2' S2 (L U R U' L U R) S2' R2'
(R U R' U) R2' D' (R U' R' D) (R' U' R2 U2' R)"
"R' F (R U R' U) (r U r' U2') F' U' R
(F' U' F U) (R' F R F') (R U R' U' R U R')"
"(L2' U S U2 S' U L) (U' L U' L' U2 L)
 U' (R U' R2 U') (R U' R' U2) (R' U2 R' U') R U' R2
U2 R' F2 (R D R' D') F2 U' (R2 U R' U' R2)
U (L U2 L' U' L U' L) (U S U2 S' U L2')"
"U' R U2' R' U' R U' R'
U L U2 L' U' L U' L'"
"L' U' L U' L' U2 L
 U2 R' U' R U' R' U2' R"
"(L F U F' U' L') (F' U' L' U L F)
 U' (R U R' U') (R' U' R U) (R U' R' U') R' U R
U' (F R U R' U' F') (R' U' F' U F R)"
"(L' U' L2 U L2' U L2 U2 L2') U2' L
 U2 (R' U' R2 U R2' U R2 U2' R2') U2' R
(S'F R f') U (R2' f R F' R) S"
"(L' U' L U' L' U2 L') (U S U2 S' U L2')
 U' (R' U' R U) (R U2' R' U') (R' U R U') R U' R'"
"U S U2 (r U2' R' U' R U' r') S'
U' S' (r U2' R' U' R U' r') U2' S
 (R U R' U) (R' U' R U') (R' U2' R U) R U' R'"
"U2 (R2 U' S' U2' S U' R) (U' R U' R' U2' R)
(L U2 L2' U2) (L2 U L2' U) L2 U' L'
U2 (R U2' R2' U2) (R2 U R2' U) R2 U' R'
U' S (L F' L f L2') U (f' L FS')"
"S' (l' U' L U' L' U2 l) U2' S
 U' (R' U' R U) (R U2' R' U') (R U' R' U) R' U R"
"U (↓ L2' U L2 U) (L' U2' L' U) (L U L' U') L2
 U' (↑R2' U R2 U) (R' U2 R' U) (R U R' U') R2"
"(R U R' U) (R' U' R2 U' R2' U2' R)
U' (R U2' R2' U' R2 U' R') (U R' U R)"
U' (↓R2 U' R' U) (R U R' U2) (R' U R2 U R2')
U M(R U R' F' R U R' U' R' F R2 U' R' U') M'
U' (L U F U' F'·L) (D L' U2' L D' L' U2' L')
"U' (l' U' L U M) (U' F L' U' L U L F' L2' U L)
 (F R U R' U') (R' F' U' F R F' U' R' U2' R)"
U' (F' L F U' L') U2' (L' U2 L U') L U2 L'
"U' (F' L F L' U2' L' U2 L) U (L' U2 L U L' U L)
U2 R' F U F (R U2 R' U') F' U'↓R' F2 R2"
"U2 (R u R' U R U' R u' R2') U' (R f R' f')
U' F' (L' U' L2 U L') (U' L' U L F) (U L U' L')
U r' U F2 U F (R' F R U) F' U2 F r"
U2 (r U R2' F' R) (U R U' R') (F R U' r')
U' (L U L' U') (L U L' U2') (L F' L F L2') (U' L U' L')
U' (l' U' L U) (l F' L2' U L U) (L' U' L F)
U' (L' U L U2') (L U F' L' F) (L U' L2' U L)
U' (F' L F L') U2' (L' U L U') (L U L2' U L2 U2 L')
U' (L F' L' F) (L F' L2' U' L U) (L F L2' U' L)
"(R' U' R U' R' U2' R) U (R' U2' R U R' U F' U' F U R)
U (F' U2 F U) (R U R' U) (R' F R F') (R U R' U' R U R')"
U' F (R U2' R' U) F' R U' r' F2 U F' U' M'
U L2' D' (l U' l' D) L2 U F U F'
R2 D (r' U r D') R2' U' F' U' F
U' (F U' F' U) (L' U L U) (L' U' L U2') F U2' F'
U' r2 D (r' U r D') r2' B (r U' r' B')
↑r2' D' (r U' r' D) r2 F' (r' U r F)
U2 (F' U F U') (R U' R' U') (R U R' U2) F' U2 F
U' (R U2' R' U2 R' F R F') (R U' L' U R' U' L)
U (R U R' U) (R' F R F') (R' U2' R2 U R2' U R2 U' R')
U F (R U' R' F) (R' F' R U2) (R' U' F' U F R) F'
(R' F R U R' U' F' U R2) (U R' U' R' F R F')
U F' R' F R2 U R2' F R F U F2
U (↑ L U' L' U2) (L2 U F U' F') L' U' L'
U2 F U (R' F R F') (R' U2' R2 U) R2 U R F'
U' (r U R' F') (R U R' U') (R' F R2 U' r')
(F' L' U' L) (F' L F L2' U2 L U) (L' U' L F)
U' (R U R' U R U2' R') U (R U2' R' U2 R' F R F')
"U2 (R f R' f') U (R2' u' R U' R U R' u R)
U2 (R' U' R U) F (R U R' U') (R' U R2 U' R' F')"
(MR U R' U) (R U2' R' U) (R' F R F' r U R')
(R U2 R' U) R' U' F U R U' F' R U2 R'
U (↑ L U L' U) (L2 F' L' F L') U2 (L U' L' U L U' L')
U2 (L' U2 L U2' L F' L' F) (L' U' L U' L' U2 L)
(R' U2' R U') (R' F' U F) U' R2 U2' (R' U' R U') R'
"M(L' U' L F L' U' L U L F' L2' U L U) M'
U2 x R2' U2' (R U R' U2) L U' R U M"
U2 (R' U' F' U F·R') (D' R U2 R' D R U2 R)
U2 (r U R' U' M) (U F' R U R' U' R' F R2 U' R')
U2 (F R' F' R U2 R U2' R') U' (R U2' R' U' R U' R')
U2 (F R' F' U R) U2 (R U2' R' U) R' U2' R
"U' (L' u' L U' L' U L' u L2) U (L' f' L f)
U2 F (R U R2' U' R) (U R U' R' F') (U' R' U R)"
U' (l' U' L2 F L') (U' L' U L) (F' L' U l)
U2 (r U R' U') (r' F R2 U' R' U') (R U R' F')
U2 (R' U' R U) (R' U' R U2) (R' F R' F' R2) (U R' U R)
U2 (R U' R' U2) (R' U' F R F') (R' U R2 U' R')
U2 (F R' F' R) U2 (R U' R' U) (R' U' R2 U' R2' U2' R)
U2 (R' F R F') (R' F R2 U R' U') (R' F' R2 U R')
U2 x' U (R U' R2' F') (R2 U' R' U') F' U2 x
U2 (R U R' U') F2 (r U r' F2) U (R U' R2' F') R
(↑R' U R U2') (R2' U' F' U F) R U R
U2 (L' U' L U' L' U2 L) U' (L' U2 L U2' L F' L' F)
U (R' F' U' F) R U F (R U R' U') (R' U R U') F'
U2 R2' F R U F' (R U R' U) F U F' U R
U2 (l' U' L F) (L' U' L U) (L F' L2' U l)
U (F R U R') (F R' F' R2 U2' R' U') (R U R' F')
"U' (L' f' L f) U' (L2 u L' U L' U' L u' L')
U' (L U L' U') F' (L' U' L U) (L U' L2' U L F)"
(↑R' U' R U') (R2' F R F' R) U2' (R' U R U' R' U R)
U' (R U R' U R U2' R2') (F R F' U2 F' U2 F)
U' (R U2' R' U2 R' F R F') (R U R' U R U2' R')
"U2 R' U2' (R2 U R' U') R' U2' (r U R U' r')
U2 (R' F R U' M' U2 M) (U' S R' F' R S')"
"U' (L F' L' S') (L F L' S)
U (S' R U' R') (S R U R')
U2 (r U R' U' M) (U R U' R')"
"U2 (R' F R S) (R' F' R S')
U' (l' U' L U M) (U' L' U L)"
"U2 M U M' U2 M U M'
M' U M U2 M' U M"
U' M U' M' U2 M U' M'
U' (M' U M U)2 M' U M
"(L' U2 L2 U F' L') (D' L2' D F L U' L')
U2 (L' U' L U' L' U2 L) U' (r U r' U R U' R' r U' r')"
"U (R U2' R2' U' F R) (D R2 D' F' R' U R)
U' (R U R' U R U2' R') U (l' U' l U' L' U L l' U l)"
U (R' U' F' U F R) U' (f R U R' U' f')
(F R U R' U' F') (R' U' R' F R F' U R)
U2 M' U' M2' U' M U2 M' U' M'
U' M' U M2' U M U2 M' U M'
U2 (F R' F' R2 U' R') (F' U' F) R U R'
↑R' U' R' (F' U' F U) (R2 U2' R' U' R)
↑ L U L (F U F' U') (L2' U2 L U L')
(R' U R U') R' F U (R' F R F') U' R' F' R2
M' U (r' F R F') U (R U R' U2) r U r'
U2 F (R U' R' U) (R U2' R2' F R F') (R U' R' F')
"U2 F' (L' U L U') (L' U2 L2 F' L' F) (L' U L F)
 U F U' (R U R' U2') R U (R2' F R F') U2 F'"
(L U2 L' U) (L' U2 L U2') (L U F' L' F)
(R' U2' R U') (R U2' R' U2) (R' U' F R F')
U2 F (R U' R' U2') (R U R' U) (R' U2' R2 U) R2 U R F'
U (R U' R2' F R) U (R U' R2' F' R) (F R' F' R)
"U' (L' U L2 F' L') U' (L' U L2 F L') (F' L F L')
 (F U R U2 R' U' R U R' F') U' (R' U' R U' R' U2' R)"
U2 (r' U r U') r' F' U' (r U2 R' U' R U' r') F r
U2 (F' U2 F U2') (R U' R' U) (R U R' U) F' U' F
U (↓B r U r' B') (r2 D r' U' r D' r2')
U' (↑F' r' U' r F) (r2' D' r U r' D r2)
U F (R' F R F') U' (F U r U2 r' U' R U R' F2)
(R U' R' U') (F U R U' R' F) (r U2' R' U') r' F R
U R' F' U2 F U' (R U R2' F R F') U2 R
(R U' R2' F R F') (R U' B U2' B' R')
U (↑R' U2 R' D' R U2 R' D R) (F' U' F U R)
U (↑ L U2' L D L' U2' L D' L') (F U F' U' L')
U2 R' F' U2 (R' F R U') (R' F' R U') F U' R
U2 (R' U2' R U') R' U' (R' F R F') (R U2' R' U2 R)
U2 (R U2' R' F) U R' U' F' U (R U' R U2' R')
U2 (R' U' R U') F U' (R' U' R U) (R U' R' U') (R U R' F')
U2 (R2 U R' U) (R' U' R U') R' F U R U' F' R'
U' (R U R' U') F' U' (R' U' F' U F R) F U2 (R U' R')
U2 F (R U' R' U) (R U R2' F') (r U R U' r')
F' (L' U L U') (L' U' L2 F) (l' U' L' U l)
U2 (L' U2 L U L' U L) (F' L F L' U2' L' U2 L)
(R U2' R' U' R U' R') (F R' F' R U2 R U2' R')
"U' (S R' F' R S') (R' F R U' M' U2 M)
(M' U2 M U) (R' F' R S R' F R S')"
U' (R U R' S') (R U' R' S)
U (R U' R' S') (R U R' S)
"(↑R2' S2 R F) U' (R' S2 R U) F' R
(r U M U R' U' r U' r') (R U R' U R U2' R')"
U' (R' U' R F D R2 D') (R' F' U R2 U2' R')
U (L U L' F' D' L2' D) (L F U' L2' U2 L)
(M' U' M U) (M' U' M U') M' U2 M
(M' U M U') (M' U M U) M' U2 M
U' (F' U' F U') (R U' R' U') (F R' F' R)
U (F U F' U) (L' U L U) (F' L F L')
(R U R' S) (R' F R f') (U R U R')
U2 (R U R' U' R' F R F') (R' U' R U' R' U2' R)
U2 (L' U' L U L F' L' F) (L U L' U L U2 L')
U' (R U' R' F) R' F' (R2 U' R' U2') (R U' R' U') R U R'
U' (R' U R U) (R2' F R F' R) U2' (R' U R U) R' U' R
"U2 (F' L' U' L U F) (L' U2' L' D' L U2 L' D L2')
U (R' F' U' F U R) U' (R' U2 R' D' R U2 R' D R2)"
U2 (F R U R' U' F') (R U2 R D R' U2' R D' R2)
(R U2' R' U') (R U R' U) (F' U F) (R U' R2' F R F')
"R' U2' (R U R' U) (F R U R' U' F2) U F R
U' (l U L' U L U2 l') U (L' U' L U L F' L' F)"
U (r' U' R U' R' U2' r) U' (R U R' U' R' F R F')
(R U R' U R U' R' U R U2' R2') (U' F' U F R)
(L' U' L U' L' U L U' L' U2 L2) (U F U' F' L')
U r' D' (r U' r' D) (R2 U' R' U) r U R'
U2 R2' D' R (F R U R' U' F') U R' D R2
R U R2' F' R U2 (F' U F U) (R' F R2 U' R')
F' U2 F U (R2 U R' U) (R U2' R2' U') F' U2 F
"U↑ L U (L F' L' F) (L' U L U') (L' U L U2' L')
U'↑r2' F2 R (F' U' F U) R' F2 r2"
U'↑R' U' (R' F R F') (R U' R' U) (R U' R' U2 R)
U2 (R U' R' U2) F' U F (R U R' U) R U R'
F R F' (r U R' U2) (r' U' r U) (r' F' U F)
(R' F R U) (r U2' r' U) (r U2' r' U') F' R U2' R'
"↓F (R U R D) (r' U' r D') R2' U' F' (U' L' U L)
(↑R' F R B') (R' D' R' D) F' (D' R U'D R U) B
U2 (↓R2 U R' U') (R' F R U R' U) (R F' R') (U' F U' F')
U' (R' U' R' F R F' U R) U' (R U2' R' U' R U R' U' R U' R')"
U2↓F R F' (r U r' U) (R' U' r U' r')
U2↓ F' L' F (l' U' l U') (L U l' U l)
(R U R' U' R' F R F') (R' U2' R U R' U R)
↓F U2' F2·U' (L' U L2 F L2' U L)
↓ F' U2 F2'·U (R U' R2' F' R2 U' R')
"(L' U2 L2 F' L' F) (L' U L U) (L F' L' F)
U2 (f U R U' R' f') U' (F R' F' r U R U' r')"
(R U2' R2' F R F') (R U' R' U') (R' F R F')
(R' U2' R2 U R2' U R U2') (R' F R F')
"(L U2 L2' U' L2 U' L' U2) (L F' L' F)
 U2 (R U2' R2' U' R2 U') (R' U' R' F' U F U' R)"
U (R U R' U) (R' U2' R2 U) R2 U R F' U F R U' R'
U2 (r U2 r' U' R U' R') (F U F' U') R' F' R
U (R U R' U) (r U2' r' U) (F' U' F U) r U r'
U2 (R U2' R') (F R U R' U' F') (U R U R')
U2 F' U2' L D (L' U2' L D') (L2' U' L U) F
(L' U' L U' L' U2 L) (F R' F' R U R U' R')
(R' F' U' F) U' (F R U R' U' F2) U2 F R
U (f' L' f U) (l U L' U' M')
U2 (F R U R' U') (R' F' r U R U' r')
U' L U L' (F' L F U' L') (U2' L' U2 L)
U2 (R U2' R' U) (R' F' U' F U R2) U R'
"U' M' U' L U· l D (l' U' l D') L2'
 U (F U R U' R' F') (R U2' R' U' F' U F R U' R')"
(↓F R U R' U') (R F' r U R2·U' r' F R F')
U2 (L U2 L' F') (L' U' L2 U L' F) (U L U L')
U' (F' L F U F' L' F) (L U L' U') (L U L' U') (L U' L')
U2 (L' U2 L) (F' L' U' L U F) (U' L' U' L)
U2 F U2 R' D' (R U2 R' D) (R2 U R' U') F'
(R U R' U R U2' R') (F' L F L' U' L' U L)
U' F (R U R' U) (R' F' U' F U R2) U2' R' F'
U' (f R f' U') (r' U' R U M')
U2 (F' L' U' L U) (r U R' U' r' F R)
U R' U' R (F R' F' U R) (U2 R U2' R')
"U2 (L' U2 L U') (L F U F' U' L2') U' L
 R' U2' R (F R U R' U' F') (U' R' U' R)"
U M' U R' U'·r' D' (r U r' D) R2
(↓ F' L' U' L U) (L' F l' U' L2'· U l F' L' F)
"U2 (R' U2' R F) (R U R2' U' R F') (U' R' U' R)
(R U' R' U) F U2' (r U2' r' U2) (R' F' R)"
U (F R' F' U' F R F') (R' U' R U) (R' U' R U) (R' U R)
U2 F (R U R' U')2 F' (r U R' U R U2' r')
U' (r' U' R U2') R' U2 F' (r U' r' F2) U r
U2 (F R U R' U') (R U R2' F R F' R U' R' F')
(R U' L' U R' U' L) U (L' U' L U L F' L' F)
(L' U R U' L U R') U' (R U R' U' R' F R F')
(F R U R' U') (R U R' F2) r U r2' F r)
U' (R U' R' F) (R U R' U')2 F' U R U' R'
(F R U R' U') (R U R' F R' F' R2 U' R' F')
R U2 (R U R' U') (R' U2' F R F') U (R2' F R F')
U' (R U R' U2') F2' U' (r' F r2 U r' F)
U' (r U r' U) (R U' R' U2') (R U' R' U2) r U' r'
U' (r' U' r U') (R' U R U2)2 r' U r
U' R' D (R' U' R UD') R U' F (R2 U R' U') F'
U R2' D' (r U r' D) (R2 f R' f')
U R2 D (r' U' r D') (R2' F' U F)
U2 R' F U R U R2' F' (R2 U' R' U') R U' F U F'
U' (R' U' F U R U' R' F' R) (F R' F' R U R U' R')
"U (L U F' U' L' U L F L') (F' L F L' U' L' U L)
 F U (R' U' F' U F R2) U' (R' U' R U) R' F'"
(F R U R' U' F') U' (L' U R U' L U R')
(F' L' U' L U F) U (R U' L' U R' U' L)
(F U R U' R') (U F' R' F R U' R' F' R)
(F' U' L' U L) (U' F L F' L' U L F L')
U' (F' U' F U) (R U R' U2) (R U2' R' U2) F' U' F
U (F U F' U') (L' U' L U2') (L' U2 L U2') F U F'
U↑R' U' (R' F R F') U R
U'↑ L U (L F' L' F) U' L'
(R U R' U R U2' R') (F' U' L' U L F)
U' (R' U2' R U R' U R) (L U F U' F' L')
"U2 (L2' U S U2 S' U L') (U F U' F' L')
(l' U' L U' L' U2 l) (f U R U' R' f')"
"U2 (R2 U' S' U2' S U' R) (U' F' U F R)
(r U R' U R U2' r') (f' U' L' U L f)"
U2 S (R' U' F' U F R) U S'
U2 S' U' (F U R U' R' F')S
"U2 (f' U' L' U L f) (L' U2 L U L' U L)
U' (R' F' U' F U R) U (R' U2' R U R' U R)"
U2 (f U R U' R' f') (R U2' R' U' R U' R')
U' (R U2' R' U) (F' U2 F) (R U' R') (F' U2 F)
(R U R' U R U2' R') U (R U R' F' U2 F R U' R')
F (R U R2' U' R) F' (U' R' U2' R)
U R' F' U' (R U R' U') R' F (R2 U' R' U) R
U2 (R U R' F') (R U R' U') (R' U' F) (U R2 U2' R')
"U2 (L' U' L F) (L' U' L U) (L U F') (U' L2' U2 L)
↑R' F (R U' R' U2') (R U R2' F' R) U R"
U (R U2' B U' B' R') U (R U R' U') (R U2' R')
"U' (L' U2 B' U B L) U' (L' U' L U) (L' U2 L)
U R' U2 F' U F (R U' R' U') (R U R' U2') R"
U R' U' R (F U R U' R' F') U' (R' U' R U R' U R)
U (R U R' U) (R' U' F' U F R2) U (R' U' R U') R'
"U' (L' u' L U') (L' U L' u) (L f' L f)
U (R' u' R U') R' U R' u R F' U F"
U (R u R' U) (R U' R u') (R' f R' f')
U (R' U' R U' R' U2' R) (F R' F' R U R U' R')
U2 (r U r' F) (R U R' U') F2 U F U' r U' r'
U F (R U' R' F) (R' F' R U2) (R U' R' F')
U2 (R U2' R' U') (R' F' U' F) (U R2 U2' R')
(R' F R U) (R U2' R2' F') (R2 U2' R' U) F U2 F'
F U (R U2' R' U' R U' R') F' (R' F R U2) R' F' R
(R U' R' U') F' U F (R' F R F' R U R')
U (F R U' R') (f U R U' R' f') U' (R U R' F')
F U2 R' F2 (R U2 R U2') R' F2 (R U' R' U') F'
U R' U' F' U F' (r U2 R U') r' F
U F (R U' R' F) U (R U' R' F') U' (R U R' F')
"U2 (F' L F L' U' L' U L) (F R U' R' U2 R U R' F')
F' U (R U R' U) M F (r U2' R' U) F"
U2 (R' F R U) (R' F' R U) F U2 F'
F R2 U2' R2' (F R' F' R2 U' R) U' R2' F'
U2 (F R' F' R U R U' R2') (U' F' U F R)
U (R' F' U' F) (R U R' F) (R U R' U') R' F' R2
"U' (F' L' U L) (f' U' L' U L f) U (L' U' L F)
U (R U2' R2' F2) U' (R2 U' R2' U) F U F R"
↑r' U' M' U2 (r' F R F') (r U2' r' U r)
U2 (R U' R' U') M' F' U2 F U R U' r'
U2 (L' U2 L U) (L F U F') (U' L2' U2 L)
U r R D (r' U r D') r' (R' U R U2 R')
U R2' U (R2 U R' U') F' U F R' U' R2
"U2 (F R' F' R U R U' R') (F' L' U L U2' L' U' L F)
U2 (R' U R U') R2' U' F' U F (R U R U) R' U' R"
U (R U R' U) (R U' R') (F' U F) (R U' R')
U2 (L F' L' U') (L F L' U') F' U2' F
F (R U' R2' F R F') U' (F R' F' R2 U R' U') F'
U2 (R U2' R2' F R F' R U2' R') (F' L' U' L U F)
"U2 (L' U2 L2 F' L' F L' U2 L) (F R U R' U' F')
U (R U2' R2' F R F' R U2' R') U' (F R U R' U' F')"
U (L' U' L U') (L F' L' F)2 (L' U2 L)
U' (R U R' U) (R' F R F')2 (R U2' R')
(r U2' R' U' R U' r') F (U R U' R')2 F'
U' (R2 D r' U2 r D' R2') U2' (R' F R F')
U (L2' D' l U2' l' D L2) U2 (L F' L' F)
U (R U2' R') (F R' F' R) (F' U F) (U2 R U' R')
U' (L' U2 L) (F' L F L') (F U' F') (U2' L' U L)
U (R U2' R2' F R F' R) U2' (R2' F' U' F U R)
U (R U R' U2') F' (r U' r' F2) (U2' R U' R')
U2 (F R U R2' F R F' R U' R') (U R U' R' F')
(R U2' R2' F R F') U2' (R' F R F')
(R U2 R' U') (F' U F U) (R' F R F) (r U r' F)
U' F (R U' R' U2) (R U R' U) (R' U' F' U F R) F'
U' F U (R' F R F') U2 (R' F R F') (R U R' F')
U F' U' (L F' L' F) U2' (L F' L' F) (L' U' L F)
(F R U R' U' F') (R U2 R' U' F' U F R U' R')
(R' F' U' F U R) U' (R' U' F U R U' R' F' R)
"U' (F R' F' R U2 R U2' R') (f' L' U' L U f)
(F U R U' R') (U F' U' R' F' r U M)"
U (F' L F L' U2' L' U2 L) (f R U R' U' f')
"(↑ L U L F' L' F U') (F' L' U' L U F2' U' F' L')
F U (R U2 R' U') (R U B' R B R2') F'"
(↑R' U' R' F R F' U) (F R U R' U' F2 U F R)
U R' F' (r U2 r' F2) (R U' R' U') (R' F R U R)
U (R' U R U2) (R' U' R U) R' U' (R' F R F2) U2 F R
F U' (R U R' U') F' U' F (R U R' U') (R U' R' F')
U F (R U R' U) (R U' R' F') U F U (R U' R' U) F'
U' (f' U' L' U L f) (L F' L2' B L2 F L2' B' L)
U' (f U R U' R' f') (R' F R2 B' R2' F' R2 B R')
U2 (L' U2 L2 F' L' F L' U2 L2) (F l' U l F2' L')
U2 (R U2' R2' F R F' R U2' R2') (F' r U' r' F2 R)
U (R' U' F R' F' R U R) F' (U' L' U L)2 F
U2 (R U' R2' D') (r U' r' D) R2 U R'
U' (R' U R2 D) (r' U r D') R2 U' R
U' R' F' U' F R' F (R2 U' R' U2) (R U R' F') R
U2 (R' F R F) U2' (R' F' R U2')↓F2 R U2 R'
(L F' L' F') U2 (L F L' U2) F2' L' U2' L
U2 (R U2' R2' F R) F2 U2 F (R U' R' U) R U' R'
U' (R2' F R F') U2 (R' U' F' U F R2) U' R' U R
"U (R U R' U) (R U' R' U) (R' F R F') U2 (R' F R F')
U (R' U' R U' R' U F' U F) (R2 U R' U' R' F R F')"
"U (L' U' L U') (L' U L U') (L F' L' F) U2' (L F' L' F)
U (L U L' U L U' F U' F') (L2' U' L U L F' L' F)"
U (R U R' U2) F2 (r U r' F) U (R' F R F')
U2 (F' L F L') U2' (L' U L U') (L F' L' F) L' U2 L
(F R' F' R) U2 (R U' R' U) (R' F R F') (R U2' R')
U2 (MR U R' U) (R U' R' U) (r U2' r' U') M'
"U (F U R U' R' F') (R U R' U R U' B U' B' R')
R U2' R2' (F R U R' U' F') U R U (R' F R F')"
"U' (F' U' L' U L F) (L' U' L U' L' U B' U B L)
U2 (R' U' F' U F R) U (R' F' U' F U' R U R' U R)"
U2 (r U R' U R U2' r') U (l' U2 L U L' U l)
(l' U' L U' L' U2 l) U' (r U2' R' U' R U' r')
"U2 (L F U F' U L' U' L U' L') (F' L' U' L U F)
U2 (R' F' U' F U' R U R' U R) U (R' F' U' F U R)"
U2 (R' F' U' F U' R U R' U R) (F R U R' U' F')
U2 F R U' R2' F2 (r U r' F) (R2 U R' U) (R U' R' F')
U2 (R U R' U) (R' F R F') U2' (R' F R F')
U (R U R D) (r' U M' U) R D' (R2' U R U R')
U2 L F (R' U' R2 U' R2' U2' R U' R U2' R') F' L'
"(F' L F L2' U' L) (F U2' F') (L' U L U') (L' U2 L)
U' (R2' F R F') U2 (R U2 R' U') (R U R' F') U2 F R"
U2 (l U2 L' U' L U' l') (L' U2 L U2' L F' L' F)
(R' U' F' U F R) U2 (R U R' U' R' F R F')
"(L U2 L' U' L U2 L2') (D' l U' l' D L2 U L')
U2 (R U2' R' U' R U2' R2') (D' r U' r' D R2 U R')"
U (R U2' R' U) F' U' F2 (R U R' U') F' U R U R'
U' F U (R U' R' U') (R U' R' F') U' F (R U2 R' F')
R' U' (R' F R F') (R U' R') (f U R U' R' f') U' R
U' (F R' F' R) U2 (R U' B U' B' R')
U2 (R U2 R' U) F2 (r U r' F) U (R' F R F')
"U' F (R U' R2' U') (F' U F U2') (R2 U R2' U) R U' F'
U' (R U2' R2' F R F' R U2' R') U f (U R U' R')2 f'"
U2 (R' U2 R' D') (r U' r' D) R F' U2 F U R
U2 r' F U' (R U' R' U2) r F U (R U' R' U') F'
(R U B U' B') (M' U M U R' U' r U' r')
U' M' U (MR U2' R2' F R F') r U2 r'
U' r U2 r' (F R' F' R2 U2' R') M' U' M
"U' (L' U' L U) (L F' L' U) (L F' L' F) (L' U2 L U) F
U2 (r' U' r U' R' U M U r) U (f U R U' R' f')"
"U2 (R U R' U') (R' F R U') (R' F R F') (R U2' R' U') F'
U (r U r' U R U' M' U' r2'x) B' U' B U L"
U2 (R U' R' U) (R U' R' U') F' U2 r' F r2 U' r' F2
(r U' r' F2) (R U' R' U) (R U' R' U') F' U2 r' F r
U2 (R U' R2' U') F' U F2 R F' U2 (R U R' U) R U R'
U' (r U2' R2' F R F' R) U' (R' U2 R U2') (r' U2 r U' r')
"(R' U' F U R U' R' F' R) (L F U F' U' L')
(R' U' F U R U' R' F' R) U' (F R U R' U' F')"
U F (R U2' R2' U') F' U F R U2 F'
U (F' L F L') (U' S L' U L S')
U2 (r' U' R' F2) R F' U r F U2 F'
F (R U' R' F) U (R U' R' F') U (R U R' F')
(R' U' F' U F R) (L' U' L U L F' L' F)
U' (F' L F L') U2 (F' L F U L2' U L2 U2 L')
U (M' U M U2) (R' F R U) F U' F'
U2 (F U R U' R' F') (R' U2' R U R' F U R U' R' F' R)
U2 (R' F R U') M' U2 r' U' F' U R
U' L F D' (L2' U2 L2 D) F2' (L' U L F L')
(R' U R2 D) (r' U r D') R2 U2' (R U' R' U2') R
U' (L' U' L U') (L F' L' F) U2 (L F' L' F)
U F U' (R U' R' F') U' F (R U R' U) (R U R' F')
U2 (R U R' U') (R U R' F') (L' U' L U') F U' R U' R'
U (F R' F' R2 U R') (F' U2 F) (R U' R' U) (R U2' R')
U (R' U2' R U R' U2' R2) (D r' U r D' R2' U' R)
U' (R' U' R' F') U' F U R2 U2' R' U2 F' U F R
U' (r' U2' R U R' U r) (R U2' R' U2 R' F R F')
"U (L U F U' F' L') U2' (L' U' L U L F' L' F)
(F U R U' R' F') U (F R U' R' U R U R' F')"
U' (R' U R2 D) (r' U r D') R2 U (R U R' U) R
U (F R U' R' U R U2 R' U' F') U' (F R U R' U' F')
U R' U F' U' F (R U R' U) F' U F R
U F U (R U' R2' F') U' F R F' (R' U' R U) R' U R
U (L U F' U' L' U L F L') (R' F' U' F U R)
U' R' F' U2 F2 U (R U' R' F') U2 R
(F R' F' R) (U S' R U' R' S)
(F R' F' R2 U' R') U' F (R U R2' U') F' U R
M' U' M U2 (r U' r' U') F' U F
U' (R U R' F') U (R' U' F' U F R) U2 F R U' R'
"U2 (F R' F' R) U2' (F R' F' U' R2 U' R2' U2' R)
U2 (F R' F' R U R U' R') U2 (R' U' R' F R F' U R)"
"U (L U F U' F' L') (R U R' U' R' F R F')
 (F U R U' R' F') U (R U R' U' R' F R F')"
U2 F (R U R' U2') (R U' R' F) (R U R' U') F' U2 F'
U' (r U' r' U) M' U2 R B U B' r'
U2 R' F' D (R2 U2' R2' D') F2 (R U' R' F' R)
U' F' U2 F U2 (r U r' U2) M' U M
U2 r' U' (r U2' r' U) (R U2' R2' U') (R U' R' U2') R U' r
U2 (l U2 L' U' L U') (M' F R' F R F2' L')
U (R' F R F' R U2 R' U' F' U') (F2 R U R' U' F')
U' F U' (R U R' U2) (F' U F U) (R U2 R' U) F'
U2 F' (r U' r' F2) U' (R U R' U2) M' U R U' r'
R' U F' U2 F U (R U R' U2) (F' U F U') R
U' (F R' F' R2 U R' U') (F' U' F) (R U R' U') (R U2' R')
U2 (F' L F L2' U' L U) (F U F') (L' U' L U) (L' U2 L)
U' (r' U' R U' R' U2' r) (l' U2 L U L' U l)
U2 (R U R' U) (R' F R U R' U' F' U R) U (R' F R F')
U' (L' U2 L U') (L' U L) (F U' F' U') (L' U L2 F' L' F)
U2 (R U2' R' U) (R U' R') (F' U F U) (R U' R2' F R F')
(R' F R U') (R' U2' R U) R2' F' R F' U F R
U' (F R' F' R U R U' R2') (F' U' F U' R U R' U R)
U (F' L F L' U' L' U L2) (F U F' U L' U' L U' L')
U2 (R U' R2' D') (r U r' D) R2 U R'
(R' U R2 D) (r' U' r D') R2 U' R
U' (L' U2 L F2) U2 (L F' L' U2') (F L F L')
U (R U2' R' F2') U2' (R' F R U2) (F' R' F' R)
L' U2 L (F' L F L') U (L' U' L U2) (L F' L' F)
(R U2' R') (F R' F' R) U' (R U R' U2') (R' F R F')
(R U R' U') R U' (f U R U' R' f') (R2' F R F')
U R' F' U' (R U R' U') R' F R2 U' (R2' F R F') U R
U2 (R' F R F') U (R U R2' F R F') U F' U F
(r' U2' R U) R' F U r F U' F'
U2 F U F' r' U' F' (R U' R' U2) r
U' (R' U' F' U F R) (r U M U R' U' r U' r')
U (R U R' U) F' (L' U2 L F) U' R U' R'
U' r D' R2' U' (R U2 R' U) R2 D r'
U' r' D (R2 U R' U2') (R U' R2' D') r
U' (R' F' U' f) (U' R U R') S' U R
U' (R B U B' U') (M' U2' R' U' R U' r')
U2 (r U2' R' U' R U' r') (f R U R' U' f')
(f U R U' R' f') (r U R' U R U2' r')
U (r U R' U R U2') (M U B U' B' R')
U (r' U' R U' R' U2') (M' U' F' U F R)
(R' F R U R' U' F' U R) U (R' U' F' U F R)
U2 (R U R' F' U' F U R U2' R') (F U R U' R' F')
"U2 (F R U' R') (F R' F' R) U2' (F R' F' R) U' F'
U L F' (L' U' L U) (F2' U F' U') (L' U2' L U L')"
U2 (F' L' U L) (F' L F L') U2 (F' L F L') U F
"U' (M' U' r' F R U F U') (R U R' U' F')
(f' U' L' U L f) (R U2' R' U2 R' F R F')"
"U (M' U l F' L' U' F' U) (L' U' L U F)
 U M' U (R U' r' U2) R' F R y' R' U R' U R"
(R' F R U) R' U' F2 U' (R U R' U R U2 R') F R
U' (r' U' M' U2) (r' F R F') U2 (R U R' U2) r
U' F (R U R2' U') F' U F (R U R' F R F') U' F'
R' (F' U' F U') (R U R' U) (F R U R' U' F') U R
U (F R' F' R) U2' (F R' F' R2 U2' R')
U (r' U' R U2) R' U2' F R F' (r U R' U) r' U r
U' (R U2' R' U2 R' F R) (S R U R' U' f')
U' F U (R' U' F' U F R) U (R U2' R' U') (R U R' F')
U2 (R U2 R' U') (F' U F U) (R' U' F' U F R2) U' R'
U' (R U2' R2' D') F' (R U' R' F) (r U r' D) R
"U' (R U R' U' R' F R F') (r' U r2 U' r2 U' r2 U r')
(F U F' U') (R' F' R) (U2 L F' L') (F R' F' R)"
U' (R U2' R' U2) (R' F R U') (R' F R F') U (R U R' F')
U2 (r U' r' F) U2 F U2 (R U' R' U') (R U R' F')
(f' U' L' U L S) (L F L' U2' L' U2 L)
U F U (R U' R2' F') U' F R F' U' R' U2' R
U' F (R U' R' U) (F R U R' U' F') (R U2 R' U') F'
"U2 (R' F R2 B' R2' F' R2 B R') (F' L F L' U' L' U L)
U (L F' L' F) (R' F' R U2) (L F' L') (U' F' U F)"
F (R U R' U2) (R' F R F') (R U2' R' U') F'
"U2 (L' U' L U L F' L' F) U2' (R U2' R' U2 R' F R F')
 (F R U' R' U R U R' F') U' (R U2' R' U2 R' F R F')"
"U (L' U2 L U2' L F' L') (S' L' U' L U f)
U (R U R' F') U' (R U R' U') (R' F R U') (R' F R F')"
U F' U' (r U' r' F2) (R U2 M' U') (r' U r U r')
U (R U R' U) (R U' R2' F') U' F U (R U2 R' F) R F'
(f U R U' R' S') (R' F' R U2 R U2' R')
"U (L' U' L U L F' L' F) (R B' R2' F R2 B R2' F' R)
(F' U' F U) (r U r' U2) (R' F R F' r U r')"
(R' U2' R U) F (R' F' U F) (R2 U R' U') F'
U2 R' D' (r U' r' F') (R U R' F) D R2 U2' R'
U F U (R U2' R' U') (R U R' U) (R' F R F') U' F'
"U2 (r U' r2' U r2' U r2' U' r) (F R' F' R U R U' R')
U' (R' F R F') (L F L' U2') (R' F R) (U F U' F')"
U2 R' U' F' U F2 (R U R' F') R U F U2 F'
U F (U R U2' R') (F R' F' R U2) (R U' R' F')
U' r U (M U R' U R U2' R') (U' R U' M') U' r'
"U F' (L' U' L U2') (L F' L' F) U' (L' U' L F)
U' (R' U2' R U R' F' U F R) (F R U R' U' F')"
U' F (R U R' U2) (R' F R F') U (R U R' F')
(r U r' U2') (R U R' U') R U' M' U' r'
U' r U (M U R' U) (R U' R' U2) r U' r'
"U' (f' U' L' U L) (S U' L' U L F)
U2↑r' U' r (U2' R' U2 R U2') r' U r"
U (f U R U' R') (S' U R U' R' F')
U' (F R U R' U') (R U2' R' U' M' U R U' r' U' F')
"U (F' L' U' L U) (L' U2 L U M' U' L' U l U F)
U2 (R U2' R' U2) (R' F R2 U R' U2') (R' F R F' R U R') F'"
"(L' U' L) (F U F') (L' U' L U2) (L F' L' F)
U2 F (R U' R' U2) (R U R' F') (R U B U' B' R')"
(R U R') (F' U' F) (R U R' U2') (R' F R F')
U (R' U' R' F R F' U R) U (R' U' F' U F R)
(R' U R2 D) (r' U' r D') R2 U (R U R' U R)
U2 (F R' F' R U R U' R') U (R U R' U' R' F R F')
(R U' R' U') M' U (R U' r' U2) (R' F R F')
(f' U' L' U L) (S L' U L U L' U' L F)
U2 (r U' r' F) U F (R U' R' U) (R U' R' F')
U' (R' U' R U') (R' F R U) R' U' F2 U2' F R
(r' U' R U) (r U2' R' U') (R' U R U2) (R' F R F')
U F' U' (L' U2 L U) (L' U' L U') (L U F U' F' L') F
U' (r' U' R U) M' U2 (R U B U' B' R2') U R
(R U R' U' R' F R) (S R U R' U' f')
R' U' F' U F2 R F' U2 (R U' R' U2) F' U F
"U2 (F r U r' U' R U' R' U' r U r') (U R U' R' F')
U l' D (l U' l U2) (l' U l U) (l' U l U') l2' D' l"
U' (l' U' L U' L' U2 l2) (U· L F' L' F U' l')
U' f (U R U' R')2 f' (R' F' U' F U R)
U' (R' U' R' F R F' U R2) (U R2' F R F2 U F)
U' (l' U' L U' L' U2 l) (f R U R' U' f')
(F U R U' R' F') U F (U R U' R')2 F'
U' L F U (R U R' U) (R U R' U') F' U2 r' x
U2 (R' F' U' F U R) U (R U R2' F R F2' U F)
U' (R' F r U) (r' F' R U2) F U (R U' R' U) F'
U F (R U R' U')2 F' (R B U B' U' R')
U (R' U' F' U F R) F (U R U' R')2 F'
U (L U F U' F' L') f' (L' U' L U)2 f
U' (L' U' B' U B L) F' (U' L' U L)2 F
U (L' U' L U) (r' U2' R U) R2' F2 R U r
U2 (R' F R F') (r U' r' U') (F' U' F U) r U2' r'
U' (R' F R U) R' U' F2 U2 F U' (R U R2' F R F') R
U' r U2' R2' F2 r F' R U2' r2' F2 R
U2 (F R U' R' U R U2 R' U' F') U (F R U R' U' F')
r' U2' (R U R') (F U F') (R U' R' F' R) U M'
U' (R' F2 R2 U2' R') (F' R U2' R2' F2 R)
(R U R2' F R F') (R U R' F) (R U R' U') F2 U2 F
U' (r U' r' F) U F U' (R U' R' U) (R U R' F')
"M U (L F' L' U' L) (F' U F) (L' U L) U2 l'
U F U2' (r U' r' U) (R' F R F') (r U2' r' U') F'"
U' (R' U R U') (R' U R U2) (R2' F R F') U F' U F R
(F R U R' U') (R U' R' U R U B' R B R2' F')
"U (F' L' U' L U) (l' U l U' L' U' L U' l' U l F)
U2 (r D' r2' U') (r U r' U) (r U r' U2') (r U' r D r')"
R U2' R2' U' F' U F R F' U2 F R U' R'
U F U (R U2 R' F) (R U R' U') F' U' (R U2 R' U') F'
U' (F R U' R' U R U R') (S R U R' U' f')
U' (r' U' F' U2) (r U' r' F2) (r U r' U' r)
U' R' U2 (R' F R F') U' (F' U' F U') R
U' (R U R' U2) (F' U' F U2) (R' F R2 U R' U') F'
U2 (R U R' U2) (F' U' F U2) (R U' R' F') U' F R U R'
R U R2' (F' U' F U) R U2 M' U R U' r'
U' (R U R' U) (R U R2' D') (r U' r' D) R2 U R'
"U (F' L F L' U' L' U L) U (L' U' L U L F' L' F)
U2 M' U' (r' F R U2) F U' (R U' R' F')"
(f' U' L' U L S) (L F L' U' L' U L)
(R' F R F') U' (S R' U' R U R S')
U F' U' F (r U M U2) R' U r U r'
M' U M U (R' F R U) (R' F R F) U' F'
U2 (L' U' B' U B M') (U l U l' U' l F U' F')
U (F' U' L U F U' F' L2') (U L U' L' U' L F)
U2 (F R U' R' U' R U R2') (F' U' F U R U' F')
U2 (F' L F L' U' L' U L) U' f' (L' U' L U)2 f
(R' F R U') (M' U2 r' F') (R F U' F')
U (F R' F' R U2 R U2' R') U (L' U2 L U2' L F' L' F)
U2 (R' F R F') U' (r U2 r' U') (F' U F U) r U r'
U F (R U' R' F) (R' F' R U2) (R U' R' U) (R U' R' F')
U2 f (U R U' R')2 f' U' (R U R' U' R' F R F')
U (F U R U' R' F') (R' F' U' F U R)
(R U B U' B' R') (F R U R' U' F')
U (r F R' U') R F' r' U2 F (R U' R' F')
U2 F' U2 F (R U' R2' D') (r U' r' D) R
U2 (R' U' F' U F R) U' (R' F' U' F U R)
(r' F' U' F U r) (F R U R' U' F')
(R U R' F' U2' F R U' R') (F U R U' R' F')
(R' F' U' F U R) U' (F R U' R' U2' R U R' F')
(r U R' U R U2' r') f' (U' L' U L)2 f
U' f (R U R' U')2 f' (l' U2 L U L' U l)
"(l' U' L U' L' U2 L) (U M U2' M' U M)
U (r' U2' R U R' U) (r2 U' r2' U r2 U r2' U' r)"
(Mr' F' r U') (R' F2 R U') M'
U2 (R U' R2' D') (r U r' D) (R2 U' R' U') R U' R'
U2 R' U F' U F (R U R' F') U F U R
"U2 (F' L F L' U' L' U L) U' (L' U' L U L F' L' F)
U F (R U' R' U') (R U R' U' R' F R F') (R U R' F')"
U2 (R' F R U') (R' U2' R U) R' F2 U F R
F (R U' M' U) (R' U R U2) r' U' (R U R' F')
(f U R U' R') (S' R U' R' U' R U R' F')
(L' U' L U L F' L') (S' L' U' L U f)
U' F U (R U2' R' U') (R U R' U) (R' U' F' U F R) F'
U (F R U R' U') (R' U R U2 r' U r U F' r' U' r)
U' (r U R' U') (M U2 R' U') F' U F R2 U' R'
U (R U2' R' U) (R U R' F) (R' F' R2 U2') (R2' F R F')
"U2 (F' l' U' l U L' U L U l' U' l) (U' L' U L F)
U' r D' (r' U r' U2') (r U' r' U') (r U' r' U) r2 D r'
U (R D' R2' U') (F' U' F U2') (R2 UD R' U') (R' F R F') 
U2 R' U F' U2' (R U R' U') (R' F R2 U R' F') U2 F R"
U' f (U R U' R')2 f' (R B U B' U' R')
U (r U R' U R U2' r2') (U'·R' F R F' U r)
(M' U M U) (R U R' U) (R' F R F') r U2' r'
U' (f U R U' R' f') (l' U2 L U L' U l)
U f' (U' L' U L)2 f (L F U F' U' L')
U2 L U2 F U (R U' R' U') (R U' R' U') F' L'
U F U' (R U R' U') F' U2 (R' F r U') r' F' R
U (F R U R' U') (R U' R' F' U' r' F U' F U r)
U' F' (L' U' L U)2 F (L' B' U' B U L)
U F (R U R' U')2 F' (R' F' U' F U R)
U' (R' U' F' U F R) f (R U R' U')2 f'
U (R U B U' B' R') F (U R U' R')2 F'
U2 r' U' (R' F2 R2 U' R' U2) r U' r' F r
U2 (R U B U' B' R') (F U R U2' R' U' R U R' F')
U2 (R' F R F') U' (F R' F' R2 U' R2) U' F' U F R
U' (r U r' U2) (r U' r' F) (R U2' R' U2) (r U2 r' F)
U (r U2' R2' F2) (r F R U2') r2' F2 R
l U2 (L' U' L) (F' U' F) (L' U L F L') U' M'
U (R' F2 R2 U2' R') (F R U2' R2' F2 R)
U2 (R' F R U R' U' F' U R) U' (r' U2' R U R' U r)
U (F R U' R' U' R U R') (F2 r U r' U' r' F r)
M U' (R' F R U R') (F U' F') (R U' R') U2' r
(R U2' R' U') (R U R2' F R F') U2' (R' F R F')
U2 (R2' F R F') U' (R U' R2' F R F' R) (U' R' U2' R)
(L F' L' F) U (S' L U L' U' L' S)
U' F U F' (R' F r U2') (M U R' F' R)
U' (F U R' U' F' U F R2) (U' R' U R U R' F')
U2 (F' L' U L U L' U' L2) (F U F' U' L' U F)
U R' U' F U F' (R U' R' F') R U2 M' U' M
U2 (R U B U' B' M') (U' r' U' r U r' F' U F)
U2 (F R' F' R U R U' R') U f (R U R' U')2 f'
(r U' r' U) (M' U2 R U) (r' F' U F)
U' (F' L F L' U2' L' U2 L) U' (R U2' R' U2 R' F R F')
U2 (R2' F R F') U2 (R' U' F' U F R2) U2' R' U2' R
U2 (F R U R' U') (R U R' U2 R' F R F' R U R' F')
U2 f' (U' L' U L)2 f U (L' U' L U L F' L' F)
"U' (F R U R' U') (r U' r' U R U R' U r U' r' F')
U2 (l' D l2 U) (l' U' l U') (l' U' l U2) (l' U l' D' l)"
U' R' F' U2 F2 U (R U' R' F') (R U R' U R)
U2 R' U' F' r' U' F U F r U' F U R
"U (F' L' U L U' L' U' L) (S' L' U' L U f)
U' (R U R' U' R' F R F') U2 (R' U' F' U F R)"
F U (R U R' F') U F (R U R' U) F'
U2 (F R U R' U') (R U R' F' U' F' r U r')
U (L' U' L U2') (F U F' U2') (L F' L2' U' L U) F
U (F' U' F U2) (R U R' U2) F' U F (R U R' F') U' F
U' (R' U' R U') R' U' R2 D (r' U r D') R2' U' R
U' (F R' F' R U R U' R') U' (R U R' U' R' F R F')
(f U R U' R' S') (R' F' R U R U' R')
U2 (R' U' R U) (F R U R' U' F') U M U' R' U r
U2 (R' U' F' U F R) (F R U R' U' F')
U2 (R' U' F' U F R) (f' U' L' U L f)
(r U R' U R U2' r2') (U' R U M' U' R' U R)
U' (f R U R' U' f') (R' F' U' F U R)
U' (R U R' U' M' U R U' r2') (U2' R U R' U r)
(R U B U' B' R') (f U R U' R' f')
(r U R' U R U2' R') (U' M U2 M' U' M)
U' (F R U R' U' F') (R U R' F' U2 F R U' R')
(l' U' L U' L' U2 l) f (U R U' R')2 f'
U f' (L' U' L U)2 f (r U2' R' U' R U' r')
(MR U R' U) (r U2' r' U) M'
U2 (F R U' R' U2' R U R' F') U (R' U' F' U F R)
U' (R' F R U) (R' F' R U2') (R F R' U) R F' R'
U' F' U' F (R U R D) (r' U' r D') R' U2 R'
U2 M' U (R U R' U) MR U2' (R2' F R F' r) U r'
U2 F' U' (L U2 L2' U' L2 U' L' U') (L F' L' F) U F
U2 F U (R' U2' R2 U R2' U R U) (R' F R F') U' F'
(R U R' F') U (R' U' F' U F R) U2 F U R U2 R'
U2 (R U2' R' U') F' U2 (R' F' U' F U R) U' F R U' R'
U (R' U2 R' D') (r U' r' D) R U' F' U' F R
U' R' U' F U R U' F2 U F (R U R' F') U' F
U' (F' L F L' U' L' U L) U (r U M U R' U' r U' r')
U' F (r U r' U2 r U) (R' U2' R U') (r' F' U' r' F r)
U2 r' (R' F2 R U') (R' F2 R2 U R' F) (r U' r' F2 r)
R' U' R F (R' F' U F) (R2 U' R' U) (R U R' F')
U F (R U' R' U') (R U R2' F') (U' F R F') R' U R
U (r U r' U') R2 D (r' U2 r D') R2' U r U' r'
U (R' F' R2 u2') (R' F' R U') (R' U R u2' R')
U (R U2 R' F) U (r U2 r' U') (R U2 R' U') R' F' R
U2 (r' U' R U' R' U2' r) U2 (R U2' R2' F R F' R U2' R')
(r U R' U R U2 r') U' (R U2' R2' F R F' R U2' R')
(r' U' r U') R' U (MR U' R' U) F' U F r
U' F (U R U2' R') (f U R U' R' f') U2 (R U2' R' U') F'
U' R2' F2 (r U r' F) (R2 U' R D) (r' U' r D') R'
(R' F R U) (R U2' R' U) (r U2 r' U') F' R U2 R'
U' (R u2' R' U') (R U R' F) (R u2' R2' F R)
U' (R U R' U) (R' U' F' U F R) F' U2 F R U' R'
(R U2' R' U2 R' F R F') (R U R' F' U2 F R U' R')
U F' (r U r' U2) r' F2 U2' (R U R' U) r
(R U2' R' U2 R' F R F') (L' U' B' U B L)
(L' U2 L U2' L F' L' F) (R U B U' B' R')
(L' U' L U L F' L2' U' L U F) (L F U F' U' L')
(R U R' U' R' F R2 U R' U' F') (R' F' U' F U R)
(R U R' U' R' F R F') (r' U2' R U R' U r)
(F R U2 R') F (R U R' U')2 F' U F'
U (F R' F' R) U2 (R U' R' U2) (F' U' F U') R U' R'
(R' F R F') U2 F' U F2 (R' F' R2 U' R')
U' (F R' F' R) U2 (R U' R' U) F2 (r U r' F)
U' (S' R U R' S U') (R' F R F')
"(F R' F' R U R U' R') (L F U F' U' L')
 (F R' F' R U R U' R') U' (F R U R' U' F')"
U2 R' U2' (F R U R' U' F2) U2 F R
U r B U' B' R' U2 (M U' r U r')
U2 (R2' F R F') (R U2' R2' F R F') (R U' R' U' R)
U2 R' U' F U R2 U' R' F' U (R U R2' F R F')
U2 (M' U' M U2) (r U' r' U2) F' U2 F
"U (R' U' F' U F R) (L F' L' U' L U F U' L')
U2 (F' U' L' U L F) U' (L F' L' U' L U F U' L')
U (R' U' F' U F R) U2 (R U R' F' U' F U R U2 R')"
U' (R' U2' R2 U R2' U F R F') U2 (R' F R F')
U' (R' F R U R') F2 (D R2 U2' R2' D') F R
U2 (M U r U2') (M U' R' U') (R' F R F') M'
U' (F' U' F U) (r U r' U2) M' U M
(F' L F L' U' L' U L) (R' F' U' F U R)
U (S L' U' L S' U) (L F' L' F)
U F U2 (R' F' U' F U R2) U2' R' F'
U' (R' U' F U) (r U2 M U) R' F' R
U F (R U' R' U') (F R U R' U' F') (R U R' F')
U2 (M' U' r' U) F U R' F R U' F' U' R
U2 M' U M U2 (R' F R U2) F U2 F'
"U' (L U F U' F' L') (R' F R U R' U' F' U R)
U2 (F U R U' R' F') U (R' F R U R' U' F' U R)"
U (L U2 L2' U' L2 U' F' L' F) U2' (L F' L' F)
U (L F' L' U' L) F2' (D' L2' U2 L2 D) F' L'
U2 R' U' F' U (L' U L U) F U (R U2 R' U' R)
"U (F U F' U') (l' U' l U2') M' U' M
U' (r' U' F U R U' R' F' r) U2 M U' M'"
(r' U' r U') R' U (r' F R F') (R' F R F') U r
U (L' U' L U' L' U B' U B L) (F' L' U' L U F)
U' (R U R' U R U' B U' B' R') (F R U R' U' F')
U2 (r' U2' R U R' U r2) U2 (R' U' R U') r'
(r U2' R' U' R U') (r2' U2' R U R' U r)
(r U M U R' U' r U' r2') (U2' R U R' U r)
U2 (r' U' M' U' R U r' U r2) (U2' R' U' R U' r')
U (R' F' U' F U R2) (U2' R2' F R F' R U2' R')
"U' (L F U F' U' L2') (U2 L2 F' L' F L' U2 L)
U2 (F R U R' U' F') (R U2' R2' F R F' R U2' R')"
(R' U' R F R' F' U F R F') (R U R' U' R' F R F')
U' (R' F R U2) (R' F' R U) (r U R' U R U2 r2) F r
U2 F U (R U' R' U) (R' F R F') (R U2 R' F') L' U L
U' (R' F R F') U' (R' F R F') (R U2' R') (F' U' F)
"U (L F' L' F) U (L F' L' F) (L' U2 L) (F U F')
U' F (R U' R' U) (R U2' R') (F' U' F') (r U r')"
U' (R' F R U R' F' R F U' S) (R U R' U' f')
(R U R2' F' U' F U R) U2' (R' F R F')
(L' U' L2 F U F' U' L') U2 (L F' L' F)
F U (R U' R2' F') U' F R F' R' U R
U' R' U' F' U F2 (R U R' F') R F U' F'
(F R U R' U' F') (R U2' R' U2 F' U2 F U R U R')
U' (R2' F R F') (R U B U' B' R') U2 (R U' R' F') U F R
(F R' F' R) U2 (R' U' F' U F R2 U' R')
(F' L F L') U2' (L U F U' F' L2' U L)
(R U2' R') (F' U2 F) (R U' R2' F R F')
U r' U' (R' F R F') (R' F R U) r F U' F'
U' (r U2' r' U2) (R' F R F') U' (F' U' F U) r U r'
U2 (R D r' U' r D' R') U' (R2' F R F' R)
U (r' U' F' U F r2) (U R' U R U2 r')
"U' (l U F U' F' l2') (U' L U' L' U2' l)
(R U R' U) (R' F R F') U2 M' U R U' r'"
U (r' U' R U M') U' (R2' F R F' U R)
"U' (l U L' U' M') U (L2 F' L' F U' L')
U' (R U B' R B R2') U' (M' U R U' r')"
U' F(S' R U' R' S) (R U2' R' U') F'
"U F'(S L' U L S') (L' U2 L U) F
U F (U R U2' R') (S' R U R' S)F'"
U' (R U2' R') (F U' F') (r U' r' U) (R' F2 R U F)
U (l' U2 L U L' U l2) (F U F' U' l')
U' (r U2' R' U' R U' r2') (F' U' F U r)
U' F (R U' R' U) (R U2' R' U2) (R' F R F' R U R') F'
U' (R' F R U') F' U' (R U R' F') r' F r2 U r'
U (r U' r' U) (r U r' U') (F U R U' R2 F' R)
U (L' B' U' B U L) (F R' F' R U2 R U2' R')
U' (R B U B' U' R') (F' L F L' U2' L' U2 L)
"U (R' U' F' U F R) (F U R U' R2' F' R U R U' R')
U (↑R' U R U') R2' F (R2 U R' U') F2 U' F U R"
"U' (L U F U' F' L') (F' U' L' U L2 F L' U' L' U L)
U2 (r U' r' U) M' U (R U' R' U2) M F' U F"
U' (M U' R' F2) (R U R' F2) r U F U' F'
U2 (R' F R U2) F U2 (R U' R' F') U' R' F2 R
r' U' (R U' R' U2') F2 (r U2 r U' r' F)
U' (R U R2' F R) F2 U' F U2 (F R' F' R)
F' (r U' r' F2') U' (R U R' U2) (R' F R F')
U' (R U2' R' U') (R' F' U' F U R) U2' (R' F R F')
U2 (F R' F' R U2 R U2' R') (r' U' R U' R' U2' r)
U' (R U R2' U') R' F (R2 U' R' U2') F R F' (R U R' F')
"U2 (F' L F L' U' L' U) (B' U' B U L)
U2 (F' L F L') U2 (F' L F L') (U L' U L)"
U' (R' F' U' F U' R) U2 (R f' U' f)
"U' (L' U L2 D l' U' l D') (L2' U2 L U' L' U2 L)
U (R' U R2 D r' U' r D' R2') (U2' R U' R' U2' R)
(R' F R U R' F' R F U' F') U2 (R' U' F' U F R)"
U' (R' F R U R' U' F' U R) (F U R' F R F' U' F')
(F U R U' R' F') U (F U R U2' R' U' R U R' F')
U' (R U2' R' U') (R U R') (F' U2 F) (R U' R2' F R F')
U2 (F' L F L' U' L' U L) U' (f U R U' R' f')
U2 F (R U' R' U') (R U' R' F') U F (R U R' U) F'
U' (R' F R F') U (R U R2' F R F2') U2' F
U2 (F' L F L' U2' L' U2 L) (l U L' U L U2 l')
U' (R U R' U) (R U R2' D') (r U r' D) R2 U R'
U' L F (R U2' R' U R' U2' R2 U R2' U R) F' L'
"U2 (F R' F' R U R U') (B U B' U' R')
U2 (F R' F' R) U2' (F R' F' R) (U' R U' R')"
U' (R f R f') U R' U2' (R' F R F')
"U (R U' R2' D' r U r' D) (R2 U2' R' U R U2' R')
(L F' L' U' L F L' F' U F) U2' (L U F U' F' L')
F (R U R' U2') (R U2 R' F') U' F U (R U R' U) F'"
U' (R' U' F' U F R) (r U R' U' r' F R2 U R' U' F')
F (R U R' U2') (R2 B U B' U' R') U' R' U F'
"U (L' U2 L U) (L' U' L) (F U2' F') (L' U L2 F' L' F)
(r' U2' R U R') (F U F' U') (R' F' R U) r"
U2 (F R' F' R U R U' R') U2 (R' F' U' F U R)
U2 F U (R U2' R' U) (R' F R F') U' F' L' U2 L
(F R' F' R) U' F' U' F2 R' F' R2 U2' R'
U' (R U R' U') (R' F R2 U R' U2) (R' F R F') (R U R' F')
U2 (r U R' U R U2' r2') (U' r U' R' U M U r)
(r' U' R U' R' U2' r2) (U r' U R U' M' U' r')
(R U2' R' F R' F' R2 U2' R') (F U R U' R' F')
U (R U2' R' F R' F') (R2 U2' R2 U') (F' U F R)
(L U L' U L U2 L2) (U' L U' L' U2 L)
(r' U' R U' R' U2') (r2 U R' U R U2' r')
U' (R U2' R' U2 R' F R F') U' (R' U' F U R U' R' F' R)
U' (r U R' U R U2' r') U' f (U R U' R')2 f'
U r2' F2 R2 U2' (r' U r U2') R2' F' r U' r
U' (F U R U' R' F') (R' F' U' F U' R U R' U R)
U (F' U' L' U L F) (L F U F' U L' U' L U' L')
U (R' U' R U' R' U2' R) U (R' F R U R' U' F' U R)
U (R U R' U' R' F R F') U' (F R' F' R U R U' R')
(R U R' U') (R' F R2 U R') d (R' U' R U' R')
F (R U2 R' U') (R' U2' R U R' U R2) U R' U' F'
(F U R U' R' F') (R' F' r U R U' r' F)
U (R U' R' U) (f R U R' U' f') (R' F R F')
(r' F R F') (r U' R' U2) (R' F R F')
(L' U2 L2 F' L' F) (L' U L U) (L F' L2' U' L U F)
(F R U R' U' F') (R U R' U' R' F R F')
"(L' U2 L U2' L F' L' F) (R U R' U R U2' R')
↓ F (l' U l F2') (L2' D' l U2 l' D L2)"
"(L' U2 L2 U L2' U L2 U2 L2') (U' L U L F' L' F)
U r D' (R U2' R' U2) (R U' R' U') (R U R' D) r'"
F U (R U' R' U) (R U2' R' U) (R U R' F')
U' (L' U2 L2 F' L' F L' U2 L) U (L' U' L U' L' U2 L)
U' (R U2' R2' U' R2 U' R2' U) (R' F R F' U R)
(R U R U') R' F U R U' (R F' R' U) (R U' R' U R)
U (R' U2' R U) (R2' F R F') U F2 (r U r' F) R
U' (f' L' U' L U f) (L' U2 L2 U L2' U L2 U2 L')
U (R U R' U' R' F R F2') (L F L' U' L' U L)
U' (R' U2' R2 U R2' U R2 U2' R') (F U R U' R' F')
U (R U R' U R U2' R') U2' (R U2' R2' F R F' R U2' R')
"U2 (R' U' R U2') (F R' F') U2' (F R F') (U2 R' U R)
U (L U2 L' U' L F U' F' L') F' (L' U' L U)2 F
U2 (r' F R U) F (R U' R' F') U' (R' F R F') r U R'"
U2 (R U R') (F' U' F) (R U R' U2) (R' F R2 U R' U') F'
U' (f' U' L' U L S) (U' L' U L)2 F
(F l' U l F2) (l F' L' F) l' U2 L
U' R' U F' U F (R U R' U R U2' R') U' R
U2 (f R U R' U' f') (r U R' U' r' F R F')
F (R U R' U') (R U' R' U) (R U R' F')
U (L' U L2 U F U' F' L') U' (L F' L' F)
"(L' U2 L U L' U L2) (F' L' U' L U F U' L')
F (R U' R2' F' R) (U2 R U2' R') (F U' F')"
U' R' F' U2 (R U R' U) R2 U2' (R' F R U2 R')
U2 (F' U' L' U L f) (R U R' U' R' F R f')
U2 (R U' R' U') (F U R U' R' F') (R U' R' U) R U2' R'
U2 (R' U' R U) (R U2' R' U2) R' U2' F R F'
U (L U L' U L U2 L') (F R' F' R U R U' R')
U2 (F U R U' R') (U2 R' F' U' F U R2 U2' R' F')
(f' L' U' L U f) (L U F' U' L' U L F L')
(R' U2' R U) R' F U F' R U F U' (R U' R' F')
U F' U' F (R U R' F) (R' F' R U') (R' F R F')
r U2 (L' U2 L U L' U L) U' r' (F R' F' R)
U2 x' U' R' F (R2 U' R' U) r' F U' (R' F R U) r x
U' (r U' r' U') (r U r' U') (R U' R' U') (F R' F' R)
U' (R U R' U R U2' R') U' (F' L F L' U' L' U L)
(L F' L' F l' U' L U L') (U2 L U L' U l)
U' (r U R' U R U2' r') U' (F' L F L' U' L' U L)
"(L' U' L U') (L' U' L U) (F U2' F' U2) (L' U2 L)
U (r U M U R' U' r U' r') (F R U' R' U R U2' R' U' F')"
U' (R' U2' R U R' U2) (F R' F' R) F' U2 F U R
(L F' L' U' L F L' F' U F) (l' U2 L U L' U l)
(R' U R U2) (R U2' R' U') (R U R' U2) (R' U2' F R F')
U (R' F R F') U' (F R' F' R2 U' R')
U↑r' F U (R' F R2 U' R2' F' R) U' r
U' (R U' R' U) (R U' R' U2) (F' U F) (R U R')
U2 F' (r U r' U') r2 F r U2 F U r
(F R' F' R U R U' x'M') (U2 L' U' L U' L')
(L' U' L U' L' U2 L) (F' L F L' U2' L' U2 L)
(F R' F' R U2 R U2' R') U (R' U2' R U R' U R)
(r U' r' U2) (M' U' R U r' U2') (F R' F' R)
F' (r U R' U2) (L' U L U') (r U' r' F) r' F2 R
(S' R U R' S) U (R U r' F R' F' r)
"(l' U' L U' L' U2 l) (F' L F L' U2' L' U2 L)
(R U2' R' U2 R' F R F')2"
U2 (↑ l F U' F' U l') U' (L2 F' L' F L')
(r U R' U R U2' r') U' (R' U2' R U R' U R)
M' U' (R' U2' R U R' U' R U R' U R)M
U F U (R U' R2' F R F) (r U r' U) r' F r
(S' R U R' S) U (R U' R' U R U2' R')
U2 (R' U' R U') R' F U F' (R' F R U') F' U2 R
(r U R' U R U2') (M U R' U R U2' R')
(l' U' L U') (L' U L U') L' U2 l
U' r' U2' (R U R' U') (R U R' U) r
U' M U (L' U' L U' L' U L U' L' U2 L) M'
"U R U' R' (L' U' L U' L' U2 L2) (F' l' U' l F L')
U2 (MR U R' U R U2' R' U M') U' (R U R' U R U2' R')"
U' r' U' (M' U' R U) (R' U' R U) r' U r
"U' (L f' L' U' L f) (L2' B' R B L)
U R' U MR U (R' U' R U') M'R' U' R"
U2 (R' U' R' F R F' U R) U2 (R U R' U' R' F R F')
U' F' (R U2' R' U2) (R' F U' F) U R2 U' R' F'
U' R' U2' (F R U R' U' F2) U F U' (R U R' U) R
U' (L' U' L U L F' L' F) U (F' L F L' U' L' U L)
(F' U' L' U L F) (r U R' U' r' F R F')
U' (L' U L U') (f' L' U' L U f) (L F' L' F)
(R U' L' U R' U L U2) (L F' L' F)
"(F' L' U' L U F) (L' U' L U L F' L' F)
 (R U2' R' U') F' U' F (R U R' U') R U' R'"
(R U2' R2' F R F') (R U' R' U') (R' F R2 U R' U' F')
"(R U2' R' U2 R' F R F') (L' U' L U' L' U2 L)
↓F' (r U' r' F2) (R2 D r' U2' r D' R2')"
(R U2' R2' U' R2 U' R2' U2' R2) (U R' U' R' F R F')
F' U' (L' U L U') (L' U2 L U') (L' U' L F)
U (R U2' R2' F R F' R U2' R') U' (R U R' U R U2' R')
"U (L' U2 L2 U L2' U L2 U') (L F' L' F U' L')
 U (R U2' R' U) F' U' F R' U' R2 U' R2' U2' R"
(R' U' R U) R' U' (R F R' U) R' U' F' (R U R' U') R'
U L U (R U2 R' F) U' (R U R' F) r U2 r2 x
U (f R U R' U' f') (R U2' R2' U' R2 U' R2' U2' R)
U' (L' U' L U L F' L' F2) (R' F' R U R U' R')
U (L U2 L2' U' L2 U' L2' U2 L) (F' U' L' U L F)
U (R' U' R U' R' U2 R) U' (R U2' R2' F R F' R U2 R')
"U2 (L U L' U2) (F' L F) U2 (F' L' F) (U2' L U' L')
U' (R' U2' R U R' F' U F R) F (R U R' U')2 F'"
U2 (R U R' U) (R' F R F') (R U2' R2' U2' R) (U R' U R)
U (f U R U' R' S') (U R U' R')2 F'
"(F' r U' r' F2') (r' F R F') r U2' R'
U' (R' F R U) (R U2' R' U') (R U R' F) (r U r' F)"
F' (L' U' L U) (L' U L U') (L' U' L F)
(F R U R' U' F') (R' U' F U R U' R' F' R)
U2 (f' L' U' L U f) (l' U' L U l F' L' F)
U' (R U' R2' U' F' U F R) U (R' F R F')
(R U2' R' U' R U' R2') (F R U R' U' F' U R)
U2 (F U R U' R' f') (L' U' L U L F' L' f)
(R U R' U' R' F R F') U f (U R U' R')2 f'
(F R U R' U') (R U' R' U F' r' U' F U r)
(R U R' U R U2') (R2' F2 r U2 R U' r' F)
U' (R' U' R U' R' U2' R) (F' L F L' U' L' U L)
"U2 (F' U' L' U L) (U2' L F U F' U' L2' U2 L F)
 U' (R' U' F' U F R) U' (F U R U2 R' U R U R' F')"
(f R U R' U' f') (R' U' F U R U' R' F' R)
U' (L F' L' F) U (F' L F L2' U L)
"U'↑ l F' U' (L F' L2' U L2 F L') U l'
(R' F R U R' U' F' U R) U' (R U2' R' U2 R' F R F')"
U (L' U L U') (L' U L U2') (F U' F') (L' U' L)
U' (r U' r' F) U F2 R' F' R2 U' R' F'
(F' L F L' U' L' U x'M') (U2' R U R' U R)
(F' L F L' U2' L' U2 L) U' (L U2 L' U' L U' L')
(R U R' U R U2' R') (F R' F' R U2 R U2' R')
(l' U l U2') (M' U L' U' l U2) (F' L F L')
(F R' F' r) U2 (R U' R' U) (R' F R F') R U2 r'
U2 R' U (F' U F U) (R U2 R' U) (R U' R' U R)
(r U R' U R U2' r') (F R' F' R U2 R U2' R')
U2 (↑r' F' U F U' r) U (R2' F R F' R)
U2 (R' F R U') (R' U' R U) R' F (r U r' U2') F R
U' F U' (R U2' R2' F R F' R) U' R' U2' F'
U' (R' U R U) (R2' F R2 U R' U' F') (R U R' U) R
(R2' F R F' R) U' (R' U R U2) R' U F' U2 F U' R
F R U' R' (r' F R F') (r U' R' U') F'
(R' F R F' r U R' U' R) (U2' R' U' R U' r')
(R U R' U) (R U R' U') (F' U2 F U2') (R U2' R')
U' (r' U' R U' R' U2' r) U' (F R' F' R U R U' R')
U (L' U' L U' L' U2 L) U (F R' F' R U R U' R')
(R' F R U R' F' R F U' F') (r U2' R' U' R U' r')
U' (R U2' R' U' R U' R') (F R U' R' U R U2 R' U' F')
U' (F R U R' U' F') (R U2' R' U2 R' F R2 U R' U' F')
U (r' U2' R U R' U r) U (R U R' U R U2' R')
U2 M U (R U2' R' U' R U R' U' R U' R')M'
U' (R' U2' R U) F (R' U R U') (R U' R' U) (R U R' F')
"(S L' U' L S') U' (L' U L U' L' U2 L)
M' U' (R U' r' U') (R U R' U) r U r'"
(R U R' U R U2') (M' U r' U R U' M' U' r')
(R U R' U R U2') (M' U R' U R U2' r')
(r U R' U) (R U' R' U) R U2' r'
U' (r U2' R' U') (R U R' U') R U' r'
U M U' (R U R' U R U' R' U R U2' R')M'
U' L' U L (R U R' U R U2' R2') (F r U r' F' R)
U (R' f R U R' f') (R2 B L' B' R')
U' r U (M U R' U') (R U R' U') r U' r'
U' (R U2' R' U' R U' R') U' (R' F R U R' U' F' U R)
U2 (R U2' R' U') F' U F (R U R' U') R U' R'
"U2 (↑ l U' l' U) (L U L' U L U') (l F' L' F) U l'
U' R' U' (F' U' F U) (R U2 R' U) (R U R' U') (R U R' U R)
(R' F R2 U R' U' F') U' (S' R U2' R' S U R U2' R') 
U2 (L' U L U) (F' U' L' U L2 F L2' U2 L)
U' x' (R U R' D) (R U2 R U) R2' D' x
U2 F (R U' R' U') (R' F' U' F U) (R2 U2' R' U') F'
(L F' L' F) U' (L' U' L U') F U' F'
U' (R U R' U') (R' U2' F R F') (R' U R U2) R' U' R
U (F R' F' R U R U' R') U' (l' U2 L U L' U l)
U' (R' U' F' U' F U' R U') (R' U' R U R' U' R)
U' (R' F R U R' F' R U F U2) (R U R' U' F')
"U F' U' F (r U R' F R' F' R2 U' r')
U (R' U' R U' R' U2' R) U' (R U R' U' R' F R F')"
(L F' L' F) (L' U2 L U) F U F'
U2 (R U R' U) (R U' R' U) R' F R (F r U r' F)
U' (r' U2' R U R' U r) (R U2' R2' F R F' R U2' R')
U (r U2' R2' F R F') (R U' R' U) R U2' r'
(R' U' F' U F R2) (U2' R' U' R U R' U' R U' R')
U (F' U' L' U L F) (L U L' U L U' L' U L U2' L')
U' (R' U2' R U R' U) (R2 U2' R2' F R F' R U2' R')
U2 (R U R' U) (R U' R' U) (R U' B U' B' R')
U2 (R U R2' F' R U') (F' U' F U2') (R' F R2 U' R')
U' (R U' R' U') R U' R' (F' U' F U2) R U R'
"U' (L U F' L' F) U (F' L F L2' U L2 U L')
U (R U2' R2' F R F' R U2') (M' U R' U R U2' r')"
U (r U' r' U') (r U r') R' D' (r U r' D) R
F U (R U2 R' U')2 F'
U' (R U2' R2' F R F) (r U2' R' U' r' F R)
U2 (R U2' R' U) (R U' R' U') (R B U B' U2' R')
U (L' U' L U) (L' U L) (F U F') (L' U' L)
U2 (f R f') (R u R' U) (R' U' R u' R')
F' U2 (F' L F L') U (L' U L U2') (L' U L U) F
(R U2' R2' U') (R U' R' U2') F (R2 U R' U') F'
U' (L' U' L U' L' U2 L) U' (L' U' L U L F' L' F)
U2 (R U2' R' U) (R U' R' U') (r' U' F' U F r) R U' R'
F U (R U' B R') (F' R B' R')
(F R U R' U' F') (L F' L' U' L U F U' L')
(R' U2' R2 U) (R U' R' U) (R U R U') (R' F R F')
L U2 (L2' U' L U) (L U' F' L' F) L U' L'
"(L' U' L U') (L' U L2 F U F') (U' L2' U2 L)
r' D (R U' R U') (R' U' R U') (R' U' R' D') r
U' (R U R' U' R' F R F') U2 (L F' L' S' L F L' S)"
U2 (f R U R' U' S') (R' F' r U R U' r')
"U (L U F U' F' L') (F' L' U L U L' U2 L U F)
U2 (f R f') U2' R2' U' (F R' F' R) U R2"
U2 (R U2' R' F') U' (R' F R U') (R' F' R U2') F
U' (R2 U' S' U2' S U' R') (U R' U' R' F R F')
U2 L U (F U F' U') (L' U2' L U') (L' U' L U' L')
U (L U2 L' U') (F' L F U' L') (U' L' U L)
U' (R U R' U') R' U2' F U R U' F' R' U2' R
F U (R2 U' R2' F') (R' U R U') F R F'
U (F R U' R' U R U R') (U R U' R')2 F'
U (F' L' U' L U F) (R U R' U' R' F R F')
U2 (R U2 R' F2) (r U2 R' U') r' F R
"F U' (R' F R f') (R U R') F'S
U' (F R U' R' U) (S' R U R' SF')
U (L' U' L F) U (F'S L' U L S')"
U S (L' U' L U L F' L' F) U' S'
U' (R U2' R' U) (R U' R' U') (R' F R F') (U2 F' U' F)
U (l' U' L U) (L' l2 F' L' F M')
U' F (R U R' F') U' (R U R' U') R' F' (r U2 R U' r')
U L U2 (L2' U' L U) (L U2 F' L' F)
U M' (F U R U2' R' U R U R' F') M
(↓R U R U' R' F) U R2 U' (F' R' U R)
U2 F U (R U R2' U') F' U F R U2 F'
U2 (L2' D' L U' L' D L2) (F U' F') (U' L' U2' L)
U (F U R U' R' F') (R' U' F U R U' R' F' R)
(l' U2 L U L' U l) U' (L' U' L U' L' U2 L)
U' (L' U2 L) (F' L F L')2 (U L' U L)
U' (L' U' L U2') F U F' (L F' L' F) L' U2 L
U' (r U R' U R U2' r') U' (r U2' R' U' R U' r')
U' (R U R' U R U2' r') U' (R U2' R' U' R U' R')M'
F (R U R' U')2 F' U (R U2' R' U' R U' R')
U' L' U2 l (F' L F l') (F' L F L') (U L' U L)
F (R U R' U')2 F' (R' U' R U' R' U2' R)
(R U' R' F R' F' R2) (U2' B U B' U2' R')
F R' F (R2 U' R' U') (R U R' F2')
↑R' U' (R U' R' U) (R' F R F')2 U R
U' (R U R' U R U2' R') U' (r U2' R' U' R U' r')
(R' U' F U R U' R' F' R) U (R U R' U R U2' R')
U2 (R' U' R U' R') (f U R U' R' f') U' R
U2 (↑r' U r U') (R' U' R U' R' U) (r' F R F') U' r
U2 (R U' R' U') (F U R U' R2' F' R2 U2' R')
U' x (R' U' R D') (R' U2 R' U') R2 D x'
U' (R U R' U R U2' R2') (F R U R' F' R F U' F')
(R' F R F') U (R U R' U) F' U F
U2 (R U R' U' R' F R F') (r' U' r U' R' U M U r)
U' (F' L F L' U' L' U L) U (r U2' R' U' R U' r')
U (L U F U F' U L' U) (L U L' U' L U L')
U' (R' F R F') U (R' U R U) (F' U F) R' U R
"U' F U F' (l' U' L F' L F L2' U l)
U' (L U L' U L U2 L') U (L' U' L U L F' L' F)"
(R' F R F') (R U2' R' U') F' U' F
U (f R U R' U' f') (R U R' U R U' R' U R U2' R')
U' (R U' R' U') F' U2 F (r' F R F') M'
U (R U2' R2' F R F') (R U' R' U) R U2' R'
U2 (R U R' U) (R U' R' U) (R U2' R2' F') U' F U R
U' (F U R U' R' F') (R' U' R U' R' U R U' R' U2 R)
U' (F U R U' R' F') (R U R' U R U' R' U R U2' R')
U2' (L' U' L U') (L' U L U') (L' U B' U B L)
U (L' U L U L' U L) F U (R U' R' U2) F'
U2 (L' U' L2 F L' U) (F U F' U2) (L F' L2' U L)
U (R' U' F R F') U' (F R' F' R2 U' R2' U' R)
U2 (R U R' U) (R U' R') (F' U2 F) (R U R' U') R U' R'
F (R' U' R2 U') (R2' U2' R U') F'
"U2 (L' U2 L U') (L' U L U) (L' B' U' B U2 L)
(R' U2 R U') (R' U R U) (R' F' U' F) U2' R"
U (L' U2 L2 F' L' F') (l' U2 L U l F' L')
U' (R U R' U') (R U' R') (F' U' F) (R U R')
"U2 (f' L' f) (L' u' L U') (L U L' u L)
F' U' F (R' u' R U') (R U R' u R)"
"F U2' (F R' F' R) U' (R U' R' U2) (R U' R' U') F'
U M U' F U (R U2' R' U')2 F' M'"
U2 R' U2' (R2 U R' U) (R U' R' U') (R' F R F') R' U R
U (R U R' U R U2' R') U (R U R' U' R' F R F')
U' (R' U' R U R') (F U R U' R' F') U (R U R' U' R)
F' U' (L' U B' L) (F L' B L)
(F' L' U' L U F) (R' F R U R' U' F' U R)
F U2 R U2' R2' F (R2 U R' U') (R U R' U') F2
"F' U (L F' L' f) (L' U' L) FS'
U (F' L' U L U') (S L' U' L S'F)
U' (R U R' F') U' (FS' R U' R' S)"
U' R' U2' R (r U R' U' r') U2' F R F'
"U' S' (R U R' U' R' F R F') U S
U' (R U R' U' R' F R F') U2 (R U R' U' M' U R U' R') M
"U (L' U2 L U') (L' U L U) (L F' L' F) (U2' F U F')
U' R' U2' (R U' R' U') (R U2 R' U') (F' U' F U2' R)"
"U' (r U R' U') (R r2' F R F' M')
U F' (L' U' L F) U (L' U' L U) L F (l' U2' L' U l)
U' M' (F' U' L' U2 L U' L' U' L F) M
"(↓ L' U' L' U L F') U' L2' U (F L U' L')
U' (R' U R U') (R2' U2' R U) (R' U R U) (F R' F' R2)"
U' R' U2' (R2 U R' U') R' U2' (F R F')
U R' U' F' U' F2 U (R U' R' F') U2 R
U2 (R2 D R' U R D' R2') (F' U F) (U R U2 R')
U2 (R' U' F' U F R) (F U R' U' F' U F R F')
R' U2' (R2 U R' U') (R' U F R F') R' U R
"(R U R' U) (R U' R2' F' U' F) (U R2 U2' R')
U (L' U' L U L F' L' F) U2' (R' F R S R' F' R S')"
U2 (f' L' U' L U S) (L F l' U' L' U l)
"U' (R' U' F' U F R) (F R U' R' U' R U2' R' U' F')
U2 (f' L' f) U2 L2 U (F' L F L') U' L2'"
U (r' F r U2) R' F (r U2 r' U') F' U R
U (L2' U S U2 S' U L) (U' L U L F' L' F)
U2 R' U' (F' U' F U) (R U2 R' U) (R U R' U R)
U' (R' U2' R U) (F R' F' U R) (U R U' R')
"U' (F' L' U L U' L' U' L) (U' L' U L)2 F
 U f (R U R' U')2 f' (R U R' U' R' F R F')"
U' (R' U' R U) (R U' R' U') (F' R' U R) (F R U R')
U2 R' U' (F' U' F U2') (R U2 R' U2') (R U' R' U' R)
U' (F R U R' U' F') (L' U' L U L F' L' F)
(r U2' R' U' R U' r') U (R U R' U R U2' R')
U (R U2' R') (F R' F' R)2 (U' R U' R')
U (R U R' U2) F' U' F (R' F R F') R U2' R'
U (l' U' L U' L' U2 l) U (l' U2 L U L' U l)
U' (R' U' R U' R' U2' r) U (R' U2' R U R' U R)M
F' (L' U' L U)2 F U' (L' U2 L U L' U L)
U R U2' r' (F R' F' r) (F R' F' R) (U' R U' R')
F' (L' U' L U)2 F (L U L' U L U2 L')
(L' U L F' L F L2') (U2 B' U' B U2 L)
F' L F' (L2' U L U) (L' U' L F2)
↑L U (L' U L U') (L F' L' F)2 U' L'
U' (R' U' R U' R' U2' R) U (r' U2' R U R' U r)
U' r' U' F (R' F R U') (R U R' F) U F r
U (L F' L' U' L F L' F' U) (L' U' L U F)
(R U2 R' U) (R U' R U) R' U F R2 F' R' U2' R2
F U' (R U R' F') U' F U' (R U2 R' U) (R U R' F')
"U (L' U' L U L F' L' F) (L F' L' U' L U F U' L')
 U' F (R U' R' U) R U R2' (F' U' F U) R U' F'"
U2 r' (R' F R F') U F' (r U' r' F2) (R U' R' U') r
F' U' F (R U R2' D') (r U r' D) R
U (L F' L' U' L F L' F' U F) U2 (F R U R' U' F')
U (L U F2' u) (L' U' L D') L2' B'
(R U R' U') R F U (R' U' R U) (R U' R' F') R'
(F R' F' R) U' (R' D' R U' R' D R2 U2' R')
U (L' U L U) (F U2' F' U2) (L U L2' U L2 U2 L')
S(F' L' U' L U F) U' S'
(R' F' U' F R) (S' R' U R S)
U↑ l U M' (F' L F L2') l U' l'
F U (R' U' R2 U' R2' U2' R2 U2' R' U') F'
"(l F U F' U' L') (U M' U2' M U M')
U2 (L2 U' L2' S' L2 S U L') (U F U' F' L')"
"(L2' U S U2 S' U L') (F U F' U' L')
U' (R U2' R' U' R U' R2') (F' U' F U R)"
(R' F' U' F U R) U2 (R U' R' S' R U R' S)
U' F' U2 F (R U R' F') U2 F U' R U2 R'
U' (R U2' R' U' R U' R') U (f U R U' R' f')
(R' F' U' F U2' R) (S' R' U' R S)
(F U R U' R' F') (R' U2' R U R' U R)
U (R U' R' S' R U R' S) (f U R U' R' f')
U (F' L F L' U' L' U L) U' (R' U2' R U R' U R)
U (R U' R' U) R U (F R U R' U' F') (R' U R U') R'
U (F' L F L' U' L' U L) (R U R' U R U2' R')
"(F' L' U L U' L' U' L S') (U' L' U L f)
U2 (R U R' U' R' F R F') U2 (R' F' U' F U R)"
(F R' F' R) U2 R U' R D (R' U' R D') R2'
U' F U (R U R' U2') (R U R' U) (R' F R F') U2 F'
U2 (R U' R' U2) (R U B U' B' U' R')
U2 (R U R' U') r' F R2 U' R' F' (L' U L U) M'
U (F' L F L') U2' (L U L2' U L2 U2 L')
(R' F R U) F U' F' (R U R' U r U2 r')
R' D' F (r U r' F2) (r U r' D) R
U2 F' U2 F (R' F R F') U R' D' (r U r' D) R
"F U' (L' U' L U) (L U F2' L' F) (U L U2 L')
U' (F R U' R' U' R U2' R' U' F') U' (F' L' U' L U F)"
U' (F R' F' R) U2 (R U' R2' F R F') U (F R' F' R)
"U2 F' (L' U' L U)2 F U' (R U2' R' U2 R' F R F')
U R' U' (R' U' F' U F R2) U' (R' U' R U) R' U2 R"
(R U R U') R' F R' U R' U' R2 U R U' F'
U (R U2' R' U') (F' U' F U) (R U' R' U) (R U2' R')
"U' (R U R' U) (R' F R F') (R2 D R' U2 R D' R2')
U2 (R' U R U') (R' U R U) (R' U F' U2' F R)"
U (R' U' R U' R' U R) (F R' F' U R) (U R U' R')
"U' (f' U f R') F U' (R' U' R U) (R' U R U') F'
(L U2 L' U' L U L' U' L U' L') U' (L' U' L U L F' L' F)"
U2 (L' U2 L F' L F L2' U2 L) (R U' L' U R' U' L)
U (R' U' R U') (R' U' R U) (F U R U' R' F') R' U2' R
U (R U2 R U) R' U' R' U2' F R F' U (R' U R U') R'
U (R U R' U') (R' F R2 U' R' F') (L' U' L U L' U L)
"U (L F' L' U' L U F U') (F U F' U' L')
(F R' F' U2') (R U R' U) (R U' R U' R')"
(F R' F' R U R U' R2') (U2' R U R' U R)
U (R' F' U' F) (R U R' U) (R U R' F') U' F U' R
(F R' F' U2') (R U R U') (R' U R' U R)
"(F R' F' U' R) U (R U R' U') (R U' R2' U2' R)
U' (R U2' R' U') (R' F R2 U R' U') F2 U2' F"
U (R U R' U) (R U' R' U) (R U' R' U') (R' F R F')
(F R' F' R U R U' R') U (R U R' U R U2' R')
U (R' U' R U') (R' U R U') (r U R' U') r' U2 F R F'
U' (L' U' L U L F' L' F) (L' U' L U' L' U B' U B L)
U2 (F U2' F' L' U L U F' L F L2') (U2 L U L' U L)
U F R F' (R U2 R' U') F' U' F (R' U R U2) R'
U' (R U R' U') (F' U2 F U) (R U' R' U' R U' R')
U2 (L F2' L2' U) (F' U F U2) (L2 F2' L')
U2 (R' U2' R U R' U R) F (U R U' R')2 F'
U2 f (U R U' R')2 f' U (R' U' R U' R' U2' R)
U' (R U R' U) (R' F R F') (r' F R F') r U2' R'
(F R' F' R U R U' R') U (R U' L' U R' U' L)
"(L' U2 L U L' U L) F' (U' L' U L)2 F
(R U2' R2' D') (R U2 R' D) (R2 U' R2' F R F')"
U2 M(R U R' U R U2 R') U (r U2' R' U' R U' R')
"U (L F' L' F)2 (L' U' L U L' U' L)
 U (r U2' R' U' R U' r') U2 (R' U2' R U R' U R)"
U (r U2' R' U' R U' r') U' (R U R' U R U2' R')
(F R' F R2 U R' U') F2' U2 L' U L
(L' U2 B' U B U2) (L2 F' L' F L' U' L)
F (R U R' U')2 F' (R U2' R' U' R U' R')
U' (R' F R U R' F' R F U') (R U R' U' F')
U2 (R U R' U) (R' F R F2) (R U2' R' U2) R' F R
F U' (R U' R' U2') (R U' R' U2') (R U' R' U') F'
U F (R U' R' U') (R U2 R' U) F' U2 F' r U r'
(R' F' U F) U R2 D (r' U' r D') R'
U' (R U R' U' R' F R F') (R' F R U R' U' F' U R)
U (R' U' R' F) R F' U2 R U2' R2' U' F' U F R U R
U' (R' F R U R' F' R F U' F') U2' (F' L' U' L U F)
U' (R' U' F2 u') (R U R' D) R2 B
U2 (R' U' R U) F (R U R' U') (R' U R U') F'
(F' L F L') U (L D L' U L D' L2' U2 L)
U' (R U' R' U') (F' U2 F U2') (R' U' R2 U' R2' U2' R)
U' S'F (R U R' U') F' U S
(L F U F' L') (S L U' L' S')
U'↑r' U' M' (F R' F' R2) r' U r
U2 (R' F' U' F U R) U' f (U R U' R')2 f'
"(r' F' U' F U R) (U' M' U2 M U' M')
U2 (R2' U R2 S R2' S' U' R) (U' F' U F R)"
"(R2 U' S' U2' S U' R) (F' U' F U R)
U (L' U2 L U L' U L2) (F U F' U' L')"
(R' U' F' U F R) U f (U R U' R')2 f'
R U2' R' F' U' F (R U2' R' U) F' U2 F
U' (R' U2' R U R' U R) U2' (R' F' U' F U R)
"(L F U F' U2 L') (S L U L' S')
U2 (R B U B' U2 R') (S' R U R' S)"
U2 (R' U' R U' R' U2' R) (F R U R' U' F')
"U' (L' U L S L' U' L S') (f' U' L' U L f)
(R' U2' R U R' U R) U2 (R U2' R2' F R F' R U2' R')"
U' (F R' F' R U R U' R') U' (R U2' R' U' R U' R')
U (R' U R U') R2' (F' U' F U) (R U' R U') R' U R
U' (F R' F' R U R U' R') (L' U' L U' L' U2 L)
(F R U' R' U R U R' S) (U R U' R' f')
U' R' U F' U' F (R U R' U) R' D' (R U R' D) R2
U F' U' (L' U' L U2) (L' U' L U') (L F' L' F) U2' F
"U2 (L' U L U2') (L' U' B' U B U L)
(R' U R U2 R' U') (F' U F U R)"
(r' F R U) F U' F' (R U R' U R U2' R') U M'
U' (F R' F' R) U2 (R' U' R2 U' R2' U2' R)
U2 (F R U' R' U' R U R' F') (R U2' R2' F R F' R U2' R')
U (R' U R U') R' U' (F R U R' U' F') (R U' R' U) R
"L D F' (l' U' l F2') (l' U' l D') L'
U (R U R' U R U2' R') U' (R' F R U R' U' F' U R)"
"(F' L F L' U' L' U L2) (U2 L' U' L U' L')
 U' (F R U' R' U' R U R' F') (R U2' R' U' R U' R')"
U' (R' F R U R' U' F' U) (F' U' F U R)
(R U' R' U) (F' U' F U) (R U' R' U') R U R'
(F' L F L' U' L' U L) U (R' U' R U' R' U2' R)
U' (F R U' R' U' R U2 R' U' F') (R' U' F' U F R)
(F' L F U L') U' (L' U' L U) (L' U L2 U2 L')
U' (L' U' L U') (L' U L U') (L' U L U) (L F' L' F)
U (R' F R U R' U' F' U R) (r U M U R' U' r U' r')
U (R U R' U' R' F R F') (R U R' U R U' B U' B' R')
U2 (F' U2 F R U' R' U' F R' F' R2) (U2' R' U' R U' R')
U (r' U2' R U R' U r) U' (L' U R U' L U R')
"U (L' U' L U) (F U2' F' U') (L' U L U L' U L)
(R U' R2' F R F') (R U R' U2) (R U2' R' U) (R U R')"
"F' U (R U R' U') (R' U' F2 R F') (U' R' U2' R)
U (F' L' U L U L' U2 L U F) U (F R U R' U' F')"
"U (F' L F L') U2' (L' U L2 F' L' F) U' (F' L F L')
(R U2' R' U2 R' F R F') U (F R' F' r U R U' r')"
"U2 F (R U R' U')2 F' U (L' U2 L U2' L F' L' F)
(R U M' U') (M U' R' U') (r U' r' U') F' U2 F"
R2' U2' (R U2 R' F) (R' F' R U) (R U R' U2) R2
"U' (L' U2 L U) (F U F' U') (L' U L U') (L' U2 L)
U (R' U2' R U R' U) (F R U R' U' F' R U' R' U2' R)"
"U (L' U' L U') (L F' L' F) (L2' D' L U2' L' D L2)
U2 (L U' L' U) (L U' L' U') (L U' F U2 F' L')"
"U' (L U L' U L U' L') (F' L F U' L') (U' L' U L)
(F R U R' F' U2 F R U' R' U) (R U R' U' F')"
"U (f U' f' L) F' U (L U L' U') (L U' L' U) F
(R' U2' R U R' U' R U R' U R) U (R U R' U' R' F R F')"
U2 (R U2' R' F R' F' R2 U2' R') (L' U R U' L U R')
U (R U R' U) (R U R2' U') F' U F (R U' R U2' R')
U' (L' U' L U) (L F' L2' U L F) (R U R' U' R U' R')
(R' U2' R U R' U') (F R U R' U' F2) U F U R
U2 (R' F2 R2 U') (F U' F' U2') (R2' F2 R)
U2 (L U2 L' U' L U' L') F' (U' L' U L)2 F
U2 f' (U' L' U L)2 f U' (L U L' U L U2 L')
"U (L' U' L U') (L F' L' F) (l F' L' F) l' U2 L
U (F R U R' U' F') (R U R' U R U' B U' B' R')"
(F' L F L' U' L' U L) U' (L' U R U' L U R')
(R U2' R' U' R U' R') F (U R U' R')2 F'
M'(R' U' R U' R' U2' R) U' (r' U2' R U R' U R)
U' (R' F R F')2 (R U R' U' R U R')
U (r' U2' R U R' U r) U (R' U' R U' R' U2' R)
U2 (F R U R' U') (R U R' U F' r2' F r U' r)
(R U2' B U' B' U2') (R2' F R F' R U R')
U2 (r' U2' R U R' U r) f (U R U' R')2 f'
(F R U R' U' F') (r U R' U' r' F R F')
(F' L' U' L U F) (R' F' r U R U' r' F)
(F' L' U' L U F2) (U R U2' R' U R U R' F')
U' R' U' R (F U R U' R' F') U2 R' U2' R
U' (R U R' U) (R' U' F' U F R) U R U2' R'
(L F' L' F) U2' (L' U L U') F U2' F'
(R' F R F') U2 (R U' R' U) F' U2 F
U' R' U' (F' R U R' U' R' F R2) U' (R' F' U F) R
U2 (F R U R' U') (R F' r U R' U' r')
U2 F (R U R' U2) (R' U2' R U) F' R' U R
U' (R' U' R U) (R' U' R U2) (R' U' R U) R' F' U2 F R
U' (R U R' U') (R U R' F' U2 F R U' R') U R U2 R'
U (R' F R U2) (R' F' R U) F (R U R' U) F'
"U (L F' L' U2') (L F L' U') F' (L' U' L U') F
U (R U2' R' U2 R' F R F') U' (L' U' L U L F' L' F)"
U f' (U' L' U L)2 (S U' L' U L F)
U' f (U R U' R')2 (S' U R U' R' F')
U2 L' U2 (l F' L F l') (F2 l' U' l F')
R U2' (r' F R' F' r) (F2' r U r' F)
U (R' U' R' F R F' U R) U2 (R U2' R2' U' R2 U' R2' U2' R)
R2 D (R' U2' R D') R2' U2 (R' F R2 U R' U' F')
U' (R' F R F') U' (F R' F' R) (S' R U' R' S)
F (R U R' F') U' F' (r U' R' U') R U' r'
U2 (R U R' U2) F' U F (R U' R' U) (R U R' U') R U' R'
U2 (r' U' R U') (R' U' r U) r' U' r f R' f'
U2 (r U R' U) (R U r' U') (r U r') (F' U F)
U2 f' U' F (L' U2 L U2) (L F' L' U2) (L' U' L f)
f U F' (R U2' R' U2') (R' F R U2') (R U R' f')
U2 (L' U R U' L U R') U' (r U M U R' U' r U' r')
(R U' L' U R' U' L) U (l' U' M U' L U l' U l)
↑R' U (R U' R' U') (R U R' U) (R' F R F') (R U R' U R)
U2 (R' F R U R' F' R F U' F') (R U2' R' U' R U' R')
"(L F' L' U' L F L' F' U F) (L' U2 L U L' U L)
U R' U' R F U (R U2' R' U2) (R' U2' R2 U) R' F'"
U (R U2' R' U') (R U R' d') r' U' (R' F' R U) r
U (R U' R' U') (S' R U' R' S) (U R U R')
U R' S U (R U R' U) (R U' R' U') S' R
(R' F' R U') (r' F rM' U') r' F2 R
l' U' l (U' L' U L)2 l' U l
U2 r U r' (U R U' R')2 r U' r'
U R U2' R2' E (R U2' R' U2) R' u U R
U (R U2 S U2) (R U2' R' U2) R' S' R'
U (R U2' R' U' R U' R') U (R' U' F U R U' R' F' R)
U' (L' U2 L U L' U L) U' (L U F' U' L' U L F L')
U2 (R U R' U) (R U' R' F') U F (R U R' U') R U' R'
U2 R' U2' (R2 U R2' U) F2 (r U' R U2' r') F
U F R2 F' (R U R' U2) (R' U R U') F' U2 F R2
U2 (r U2 R' F) (R' F' R U') (R U R' U2) (r' F R F')
U (R' F R F') U (R U R' U) (r U' r' U) r U r'
U2 R U2' R2' F' U' F R (F' U F U') R' U R
U' (R' U' R U' R' U2' R) U' (R U2 R' U2' R' F R F')
U (L U L' U L U2 L') U (L' U2' L U2 L F' L' F)
U (↑R' U' R U' R') (F R' F' R) U' (R U' R' U) (R U R' U') R
U' (S' R U R' S) (R' F R F') U (F R' F' R)
U R F U R2' U' R F' (R U R' U') R2
(R' U' R' F R F' U) (R2 U R' U R U2' R')
U (F R U R' U' F') (R U2 R' U' R U R' U' R U' R')
U2 R' U' (R' F R F') (R U' R' U2 R)
"U2 (L' U2 L U L' U L) (f' L' U' L U f)
(R' U2' R U R' U R) U' (R' U' F' U F R)"
U2 (R U2' R' U' R U' R') (f R U R' U' f')
"(L U2 L2' U' L2 U' L') (F' L F L2' U2 L)
 (R' F R U) R' U' F' (R' F R U) (R U' R' F') R"
(R' U2' R2 U R2' U R) (F R' F' R2 U2' R')
U2 (R' F' U' F U R2) (U R' U R U' R' U R U2 R')
U2 (r U2' R' U' R U' r') U2 (R' U' R' F R F' U R)
U' F U F (R U' R' F') U2 (R U' M' U' r')
(R' U2' R U R' U R) U (R U R' F' U2 F R U' R')
U2 R f U' R' U S' (R U2' R' U') S R f' R'
U' (F' r U R' U' r' F R) (F R U R' U' F')
U (F R' F' r U R U' r') (F' L' U' L U F)
"U2 (F R' F' R U2 R U2' R') U (R U R' U' R' F R F')
U (r U' R' U2 R U r') U (R B U B' U R')"
U' (F' r U R' U' r' F R) (f' U' L' U L f)
"U (F R' F' r U R U' r') (f U R U' R' f')
 F (R U R' U) R' D' (R U2 R' D) R F'"
U' (F' L F L' U' L' U L) (F' U' L' U L F)
U (F R' F' R U R U' R') (F U R U' R' F')
R' U' R F (R U' R2' U2') (R2 U R' U) (R U' R' F')
U (R' U' R U) (R' U2' R U2) (R' U R U) R' (F R' F' R2)
U' (R U2' R' U') (R' F' U' F U R) U' R U' R'
U' R' U2' R (f U R U' R' f') U2 R' U R
"U R' F (D R2 U R2') (D' R U' R') F' R
U2 R2 D (r' U' r D') R2' (U' F' U2' F)"
U (R' F R U R' U' F' U R2) (U R' U R U' R' U R U2' R')
(R U R' U') R U2 (R2' F R F' R) U' (R' U' R U2) R'
U2 (R U' L' U R' U' L) (f U R U' R' f')
U F (R U' R' U2') (R U R' U) F' (R' F R U') R' F' R
U' (R U2' R' U2) (R' F R2 U R' U') F'
(R' F' U' F) U' R U2 F U' (R' U R U) F'
U2 (R U' L' U R' U' L) (F' L' U' L U F)
U2 (R U R' U R U2' R2') (U' F' U' F U R U2 R' U' R)
U2 (R' U' R U' R' U2' R) U (R U2' R' U2 R' F R F')
U (R' F R U) R' U' F' (R U' R' U) (R U' R' U2') R
U2 (R' U' R U) R' U' (R' U' F' U F R2) U2' R' U2' R
"U' L F' (D' L2' U' L2) (D L' U L) F L'
U2 L2' D' (l U l' D) L2 (U F U2 F')"
U F (R U R' U) (R2 U R' U) (R U2' R' U) R' U2' F'
U (R U R' U2) F' U F (R U' R2' F) (R U R U') R' F'
U2 (L' U R U' L U R') (f' U' L' U L f)
U2 (r' U' R U') (R' U R U') (R' U r' D') (r U r' D) r2
U (L' U2 L U2') (L F' L2' U' L U) F
U' F (R U R' U) F' U' F R' U' R F' R' U R
U2 (L' U R U' L U R') (F R U R' U' F')
U2 (L' U' L U' L' U2 L2) (U F U F' U' L' U2' L U L')
U2 (L U L' U L U2 L') U' (L' U2 L U2' L F' L' F)
U2 R' U2 (F' U F U') (R U R' U') (R U' R' U') R
U' (r' U r U') r' (R' F R F') (R U' R2' F R F' r)
(R U R' U R U2' R') U (r U r' U R U' M' U' r')
"(L' U' L U' L' U2 L) U' (l' U' L U' L' U2 l)
 (r U' r U') (r2' U' r2 U) r2' U r U r'"
(R U R' U R U2' R') U (r U R' U R U2' r')
U2 (r' U' r U' R' U M U) (r2 U2' R' U' R U' r')
"(r U r' U R U' M' U' r2') (U2' R U R' U r)
U2 (l U l' U L U' M U') (l2' U2' L U L' U l)"
U' F (R U R' U2) (R' U R U) F' R' U2' R
U2 R' U' (R F R' U) R2 U2' (R' U' R U) R' F'
U' (R U R' U R U2' R') U' (r U R' U R U2' r')
U' (R' U' R U' R' U2' R) U (r' U' R U' R' U2 r)
U' F' (U' L' U L)2 F
U2 R' U' (F U R U' R' F) (r U2 R U') r' F
U F (U R U' R')2 F'
U2 (R U R' U' R' F R F') (L U L' U L U2' L')
U2 (L' U' L U L F' L' F) U' (L U2 L' U' L U' L')
U2 (R U R' U' R' F R F') U (R' U2' R U R' U R)
U2 (L' U L) (F U F' U2') (L' U' L U) (L' U' L)
U2 (R U' R') (F' U' F U2) (R U R' U') (R U R')
(R' F R2 U R' U) (r U r' U2) F2 U2' F
U' R' U' F' U2 F (R' F R F') U2 (R U' R' U2') R
(F U R U2 R' U' R U R' F') (R U R' U R U2' R')
r' U' (R U' R' U2') F' (r U r U' r' F)
U2 (r U R' U R U2' r') U2' (R U R' U' R' F R F')
U2 F' U' F (r U' r' U) (r U' R' U') R U' r'
U2 F U F' (R' F R U') R' F (r U r') F R
U2 (f' U' L' U L f) (L U L' U L U2' L')
U2 (f U R U' R' f') (R' U' R U' R' U2 R)
(F U R U' R' F') (r U R' U R U2' r')
"U' (L' U' L U') (L F' L' F') (R' F' R F')
U2 (r U2' R' U' R U' r') U (R' F' U' F U R)"
U (R U R' U) (R' F R F) (L F L' F)
"(f' U' L' U L f) (L' U' L U' L' U2 L)
U (R' F' U' F U R) U (R' U' R U' R' U2' R)"
(f U R U' R' f') (R U R' U R U2' R')
"U (R U R' U) (R U' B U' B' R')
U' (R' F' U' F U') (R U R' U R)"
(F' U' L' U L) (U' L F' L' F L' U L F)
(F U R U' R') (U R' F R F' R U' R' F')
U (F' L' U L F R U' R') U (l U L' U L U2 l')
U' (F R U' R' F' L' U L) U' (r' U' R U' R' U2' r)
(R U R' U' R' F R F') U (R' U' R U' R' U2' R)
U' F' (R U2' R' U2) R' F U' F U R U' F'
U2 (F' L F L') U (L F U F' U' L2' U' L)
"U2 (F R' F' R) U' (R' F' U' F U R2 U R')
F U R' U' R F' (R2' F R F') U R"
(L' U' L U L F' L' F) (R' U2' R U R' U R)
(R U R' U' R' F R F') (L U2 L' U' L U' L')
"U2 (F' L F L') (f' U' L' U L f) (U L' U' L)
U' (l' U2 L U L' U l) U' (L' U' L U L F' L' F)"
"U2 (F R' F' R) (f U R U' R' f') (U' R U R')
U (r U2' R' U' R U' r') U (R U R' U' R' F R F')"
(R' U' R U') R' U F' U' F2 U (R U' R' F') U2 R
F U (R U2' R' U') (R' U2' R U R' U) (R2 U R' F')
(F R U' R' U' R U2' R' U' F2') (U' L' U L F)
R (F R U R' U' F') U (R' U R U') (R' U2' R U' R')
(F' L' U' L U F) (R U' L' U R' U' L)
(f U R U' R' f') (R U' L' U R' U' L)
(r U r' U') r U2 (R2' F R F') U2 R U' r'
(R' F' R U) R' F' U' (R' F R U) F' (r U2 r' F) R
(R' F' R U') R' U' (F U R U' R' F) (r U2 r' F) R
(R' F R F') U' (F R' F' R) U' (R' F R F')
U (↓R U2 R U2') (R2' F' U' F) (R U F R' F')
U2 (R U' L' U R' U L) U (F R U R' F')
U' (R U2' R' U2 R' F R F') U2 (R' U'↑R' F R F' U R)
F' U' (L' U L2 F) (L' U2 L' U2 L)
(R U2 R' U2') (R U' R' U') (R' F R F') U2 R U' R'
F' U' (L' U L U') (L' U L2 F) (l' U' L' U l)
(f' U' L' U L f) (L' U R U' L U R')
(F R U R' U' F') (L' U R U' L U R')
(R' F' R U) (R' U' R' F) (R2 U' R' U) F' U F R
(r U2 r' U2') (R U' R' U') F' U' r U' (L' U2 L U) r'
(L F' L' F) U (F' L F L') U (L F' L' F)
U' R D (r' U r D') R2' U F' U2 F U R
U' (R U' R2' U') F' U F (R U2 R U) (R' U' R U' R')
U2 (L' U R U' L U' R') U' (F' L' U' L F)
F U (R U' R2' F') (R U2 R U2' R')
(r U R' U') MR U (R' F' U' F) U' R U2 R'
F U (R U' R' U) (R U' R2' F') (r U R U' r')
U' R U2' R2' u' (R U' R' U) R' u R
U' (R' U2' R2 u) (R' U R U') R u' R'
(R U R' U') (R' F R U2) F' U' (R' F U' F' U R)
(l' U' L U' L' U2 l2) (U M' U L' U' l U' l')
(r U R' U R U2' r2') (U' M' U' R U r' U r)
U'↑R' U' (F R' F' R)2 U R
U↑ L U (F' L F L')2 U' L'
U (L U F' L F L' U' L') (F U R U' R' F')
U' (R' U' F R' F' R U R) (F' U' L' U L F)
(r U r' U2) r U2' (M U' R' U') (R U M' U r')
U2 (R' U2' R U R' U R) U (R' F2 r U r' F R)
U' (R' U2' R U R' U R) U (r' U2' R U R' U r)
U2 R f R' S' (U R U2' R') S U' R U f' R'
U (R U R' U' R' F R F') U' (F R' F' r U R U' r')
"U' (L' U' L U L F' L' F) U (F' L F l' U' L' U l)
U (R' U2' R U) F U' R' U2' F R F' (R U R' F')"
U' F R U' B U B2 R' F' R B R'
(R' F2 r2 U' r') F U2 (R U' r' F)
U2 (f R U R' U' S') (R U' R' U R U R' F')
(R' U' F U R U' R) (B' R2' F' R2 B R')
(R U2' R2' U') (R U' R' U2') F R F'
"(L' U2 L2 U) (L' U L U2) F' L' F
 U2 (R' U2' R2 U) (R' U R U2') f' U' f"
"U (R U' B U' B' R' U') (r U' R' U2 R U r')
U2 (F R' F' R U R U' R') U' (R U2' R' U2 R' F R F')"
U' (F R' F' R U2 R U2' R') (f U R U' R' f')
U (F' L F L' U2' L' U2 L) (f' U' L' U L f)
U F U' R2 D (R' U2' R D') R2' U F'
U2 (L' U2 L U L' U L) U' (L' U2 L F' L F L2' U2 L)
"U2 (R U2' R' U' R U' R') U (R U2' R' F R' F' R2 U2' R')
U' R' F R U R' F' R y' R2 D R' U' R D' R2"
U (R B' R2' F R2 B R2' F' R) (F R U R' U' F')
U (F' L' U' L U F) (L' U2 L2 U L2' U L2 U2 L')
U (F R U R' U' F') (R U2' R2' U' R2 U' R2' U2' R)
U2 (F U' R U' R' F') U' (R' F R U2' R' F' R)
U2 (F' U L' U L F) U (L F' L' U2 L F L')
U2 (R' U2' R U R' U R) (F' L F L' U' L' U L)
U' L F' U' (L' U L2 F L2') (U' L U L')
U' R' F U (R U' R2' F' R2) (U R' U' R)
U (L F' L' U' L U F U' L') U (L' U' L U' L' U2 L)
U (R' F R U R' U' F' U R) U' (R U R' U R U2' R')
U' F U R2 D (R' U' R D') R2' U (R U' R' F')
U2 (R U' r' U) (R U R' U') M' U' (F R' F' R)
U (L F' L' U' L U F U' L') (R U2' R' U' R U' R')
U (R' F R U R' U' F' U R) (L' U2 L U L' U L)
U (R U' R' U) (R U' R' U') R U (f R U R' U' f') R'
U' (F R' F' R2 U R') (F' U' F U2') (R U' R')
U' (F' L F L2' U' L) (F U F' U2) (L' U L)
U (r U M U R' U' r U' r') U' (R' U' R U' R' U2 R)
U (R' U2' R U R' U R) U (r U r' U R U' M' U' r')
U (R' U2' R U R' U R) U (r U R' U R U2' r')
U (R' F R U) (R U' R2' F') (R2 U' R' U) R U R'
U' (r U M U R' U' r U') (M U2' R' U' R U' R')
F R U' R' (f U R U' R' f') U2 (R U2' R' U') F'
"U (R U' F R2' U) (·R' U' R2 F' U2') (R2' F R F')
U (r U2' R' U') (MR U R' U') r U' r'
F' U' (L' U2 L U') F R U' R'
(r U R' U') (r' F R2 U R' U' F')
(r U2' R' U' R U' M) (U R' U' R' F R F')
U (F R' F' R) (U R U R') (F R' F' R) (F R' F' R2 U2' R')
S (R U R' U') (R' F R2 U R' U') f'
"U (L' U' L U') (L U F U' F' L2') U L
 U' R' U' R (F U R U' R' F') (U' R' U R)"
U (L' U' L U') (F R U' R' F') (L' U2 L)
U2 (R U R' U' R' F R F') U' (R' U' R U' R' U2' R)
U2 (F' L' U' L U) (L' U L U L' U2 L U F)
U' (R' U' R U') R' U F' U (R U R' U') (R' F R U) R
U (R' U' R U) R' U' (R' U' F' U F R2) U' R' U R
(R U R' U') (R' U R U) (R U' R' U) R' F' U2' F R
U (R U2' R' U') (R U R2' F R F') R U2' R'
U' (R' F' U' F U R2) (U2' R2' U' R2 U' R2' U2' R)
"U2 L F' L F (L2' U' L·U L F' L' F) L'
(R U R2' F R F') (R U2' R' U') F' U2' F"
(L' U' L U L F' L' F) (L' U R U' L U R')
F' (R U2' R' U2) R' F2 (R2 U R' U') F'
U' (R' U' R' F R F' U R) U (R' U' R U' R' U2' R)
U2 (R U2' R' U' R U' R') U (R' U' F R' F' R U R) 
U (R U2' R2' U' R2 U R2' U' R2 U' R2') F' U F R
U2 (R U2' R' U' R U' R2') (U' F' U F R)
U (R U R' U) (R U' R' U) (R' F R F') (R U2' R')
U' (R U R' U) R' U' R2 U' R2 U (R' F R F') U R
U' l' U2 L (F' L F L') U (L' U' L U) L' U l
U2 (R U R' U2) (F' U' F U2) (R' F R F')
"F' U' (L F L' F') (L' U L U') (L' U L2 F L')
U' (R' U' R F') U' (R U R' U') (R' U2' F2 R F')"
"U'↑r' U' (R U' R' U) r' D' (r U r' D) r2
U (l' U' L U' L' U2 l) U (L' U' L U L F' L' F)"
U (R U' R' F) R' F' R2 U2' (R' U R U) (R' U' R U2) R'
U' F' U2 (R' F' R U') (R U R' U2') F U R' F R
U2 (L F' L' U' L U F U' L2') (U' L U' L' U2 L)
"(L' U' L U L F' L' F) U (L U2 L' U' L U' L')
 U2 (F R U' R' U R U R' F') (R U2' R' U' R U' R')"
U2 (R' U F' U' F R U R' U2' R) U (f U R U' R' f')
↓r R D (R' U R D') r' U R' (U' r U' r')
(L' U' L U L F' L' F) (L' U' L U' L' U2 L)
(r U' r' F) U2 F U' (R U' R' U) (R U' R' F')
U2 (F R U' R' U R U2' R' U' F') (R' U' F' U F R)
F' U' (L' U L2 F L') (U' L' U L)
U2 (R U R' U2) (F' U F) (R U' R' U) (R U' R')
U' (L' U R U' L U2) (R' U' R' F R F')
U2 (f U R U' R' f') U' (F R U' R' U' R U2' R' U' F')
U2 (R U B U' B' R') (F' r U R' U2 r' F2 R)
U (R' U2 R' D') (R U2 R' D) (R U' R' F) R F' U R
(F' L F L' U' L' U M') (U' L U' L' U2 l)
U' (R' U' F U R U' R' F' R) (F U R U' R' F')
U (R' F' U' F U R) U' (F' r U R' U' r' F R)
U' R' U (F' U F U) (R U' R' F') U2 F U' R
U (R' U' R U2) (R U2' R' U') F' U F (R U' R2' U2' R)
(R U2' R' U2) (R U' R') (F' U' F) (R U R')
U F' U' F (MR U' R' U) r U R'
(r' F R U) R' (F U' F' U) R U' M'
F (R U' R' U') R U R2' (F' U' F U) R2 U' R' F'
U2 (R' U' R U') (R' U' R U2') R2' U' F' U F R U R
U2 (F U R U' R') (U R2 D R' U2' R D' R' U R' F')
R2 D' (r U2 r' D) R U F' U F R
U2 (↑ L2 F2' L' F') U' (R U' R2' F' R) U L'
U2 (r U2 R' U') (R U R' U') R2 U' r' F U R' U' F'
(R' F R U) (R' F' R) (F U' F')
U2 (R' F R U) (R U2' R2' F' R2 U2' R') (F U' F')
U2 (R' F2 R U2) (L F' L' U') (L' U L U') F (U L F L')
F U (R U' R2' F') (R U2 R U') (R' U R U2) R'
U (R' F' U' F) (R U R' F') (R U R' U') R' F R2
(R U R' U) (r' U' R2 U' R2' U2' r)
U (F U R U' R' F') U' (R' U' F R' F' R U R)
U' (R' U2' R U R' U R) U (r' U r2 U' r2 U' r2 U r')
U2 (r' U2' R U) M' U' (R' U R U') R' U M U r
"U2 (F' L' U L U2' L' U' L) (U' L' U L F)
U R' F' (R U2' R' U' R U' R') U2' F R"
"U' (R' U' F R' F' R U R) (L U F U' F' L')
U' (R U r' U) (R U R' U') (r U R' U) R U R'"
F' U' (r U' r' F2) (R U2 R' F') U F
"F' U (L' U' L U2') (L' U' L U')2 F
 U' R' U F' U2 (R U2' R' U' R U' R') F U' R"
U' (f R U R' U' f') (R' U' F' U F R)
U2 (R U R' U R U2' R') U f (U R U' R')2 f'
(R U R' U) (r' u' R U') R' U R' u r
F U (R U2' R' U') (R U R' F')
(l' U' L U) (l F' L2' U' L U F)
"(l' U2 L U L' U M) (U' L U L F' L' F)
 U (R' U2' R U) (R' U' R U) y (r U' r' U) r U r'"
"U' (F' L F L') (U' L' U' L) (F' L F L') (F' L F L2' U2 L)
U (F R' F' R) U' F2 (r U r' F) U' R U2 R'"
S' (L' U' L U) (L F' L2' U' L U) f
U' (R U R' U) (R' U' F' U F R2) U' R'
"U' (R U R' U) (F' L' U L F) (R U2' R')
U' (R U R' U') (R U R') (F' U2 F) (R U2' R')"
U2 F' U' F (r U' r' U) r' U r2 U r2 U' r
U2 R' F' (L' U2 L U) (L' U2 L U') F U R
"U2 (L' U' L U L F' L' F) U (L U L' U L U2 L')
 (F R U' R' U R U R' F') (R U R' U R U2' R')"
U2 (F R U R' U') (R U' R' U' R U2' R' U' F')
U2 F (R U R' U) (r U' r' U') r F (R U' R' F') r'
U' (L' U2 L U) (L' U' L2 F' L' F) L' U2 L
"U (L F U F' U' L2') (U2 L2 U L2' U L2 U2 L')
 (r' U2' R U R' U r) U (R' U' R' F R F' U R)"
U2 F U (R U' R2' F2) (R U2 R U2') R' F
U2 R' F R' F' (R2 U R'·U' R' F R F') R
(R U R' U' R' F R F') (R U' L' U R' U' L)
"U (L U L F' L' F U' L') U' (L U L' U L U2 L')
U2 R' D R2' (F R U R' U' F') U R2 D' R"
"U2 (L' U2 L U L' U L) U' (L U F' L F L' U' L')
U' (R' U' R' F R F' U R) U' (R U R' U R U2' R')"
"U' (L' U2 L2 U L2' U' L2 U L2' U L2) F U' F' L'
 F (R U' R' U2') (R U R' U) (R' F R F') (R U' R' F')"
"U2 (L' U2 L U L' U L2) (U F U' F' L')
 U (R U R' U R U2' R') U (R' U' F' U F R)"
"U' (L' U' L U') (L' U L U') (L F' L' F) (L' U2 L)
U' (R' U' F' U F R) F (R U R' U')2 F'"
U r' U2 F' U (R' U2' R U R' U R) U' F U2 r
"U r U2' R' (F R' F' R) U' (R U R' U') R U' r'
U (R U R' U R U2' R') U' (R U R' F' U2' F R U' R')"
U2 (r U' r' F U2 F U2) (R U R' U' F')
"F U (R' F' R F) (R U' R' U) (R U' R2' F' R)
U (L U L' F) U (L' U' L U) (L U2 F2' L' F)
(R' U' R U2') (F R' F') U (F R F') (U2 R' U R)
"U↑ l U (L' U L U') l D (l' U' l D') l2'
U' (r U R' U R U2' r') U' (R U R' U' R' F R F')"
R F U R' U' F' U2 (R U2' R' U') R2 U' R2'
(r U' r' F) (R U R' U') R F' (r U R2' U) R U' r'
U2 (R' F R U R' U' F' U R2) (U R' U R U2' R')
U (F R' F' R U2 R U2' R') U2 (R' F' U' F U R)
(R U R' U' R' F R F') U' (R' U2' R U R' U R)
↓ l' L' D' (L U' L' D) l U' L (U l' U l)
(R U R' U' R' F R F') (R U R' U R U2' R')
U' (F R U R' U') (R U R' U F' U2 F' r U r')
"U2 (F' L' U L U' L' U2 L U F) (L U F U' F' L')
 U R' U' R (F U R U' R' F') U2 (R' U R U') R' U2' R"
U' F U F' (ML' U L U') l' U' L
U r' D' (r U' r' D) r U (F R' F' R)
U F (R U R2' U') F' U F (R2 U' R' U) (R U R' F')
U' (F' U F U') (R U' R' U') (R U R' F) R' F' R
U' (R' F' U' F) U' R' D' (r U2 r' D) R2
"U2 (F' U' L' U L) (U' L2' D' L U2 L' D L U' L F)
U' (F R U R' U') (R' F' R2 U R' F' U2 F R U2' R')"
U2 (↑R2' F2 R F) U (L' U L2 F L') U' R
U F' (R U2 R' U') F2 U' F' U (R U R' F') U' F'
(L F' L' U') (L F L') (F' U F)
"U2 (L F' L' U') (L' U2 L2 F L2' U2 L) (F' U F)
(r U' r' F) (R U R' U') (R' F' r U2) R U' r'"
"U2' (L F2' L' U2') (R' F R U) (R U' R' U) F' (U' R' F' R)
U2 (↑R2' F R2 U R' U') F' U2 (R U2' R' U') (R U R' U2' R)"
F U (R U' R' U) (R U' R2' D') (R U R' D) R U' F'
U2 (r' F' U' F U r) (F R' F' R U2 R U2' R')
F U (R U' R2' F' R) (U R U' R')
"U2 (L' U' L U2') (F U' F') (L' U L U') (L' U L)
(R' U' R U) R' U (F U R U' R' F') (R U' R' U R)"
U (R U' L' U R' U2') (L U L F' L' F)
(R' U' R' F') (R U R U') R' U' F U' (R U R' U) R
U2 r' U' (M' U R' D') (R U2 R' D) R2 U r' U r
(F R' F' R U R U' M') (U R' U R U2' r')
U (L U F' U' L' U L F L') (F' U' L' U L F)
U' (r U R' U' r' F R F') U' (F R U R' U' F')
F U' (R U' R' U') F' U F (R U2 R' U) F'
U (R U R' U2) (R' U' F U R U' R' F' R2) U2' R'
U2 (R' U2' R U2) (R' U R U2) (R' F' U F) U R
U2 (R U R' F') U2 F U (R' F R F') R U2 R'
U' M' U' F (R U' R' F') r2' F r U' F R
U2 (R' U' R U') (r U R2' U) R2 U2' r'
U' (F' U' L' U L F) U (L U F' L F L' U' L')
U' (R U R' U2) F' (r U' r' F2) U' R U2 R'
U2 (F R U' R' U2 R U R') (U R U' R' F')
U (L U F' L F L' U' L') (R' U' F' U F R)
(r U' r' U) (R U R' U r U2 r') (U r U r')
F U' (R U R' U2) (R U R' U)2 F'
U (R U R' U) (R' F R F') (R U' R' F') U2 F R U' R'
"U (f' L' U' L U f) (L U F U' F' L')
 U2 (R' U' F' U F R) U2' (F U R U' R' F')"
U' (r' U2' R U) R' F U r F (R U' R' F')
U' L U2↑ L2 U2 F' L' F (U2' f U f')
U' (R' U' R' F R F' U R) U' (R U R' U' R' F R F')
"(l F l2' U' L U) (l F' L2' U' L F)
U2 (R2' F R F') (R U2' R' U) (R U2' R' U' R)"
(F' U2 F U) (L F' L' U L F L')
U' (R U R' U) (R U' R' U') (R U' R' F') U' F R U R'
(L' U L2 F' L' F) U' (L' U' l U L' U' L M')
U (R U2' R' U' R U' R') U' (R U R' U' R' F R F')
U (f' L' U' L U f) (L' U R U' L U R')
U2 R2' F2 R U' F (R' F R F' R U R') F2 R
U' R' U' F2 U' (R U R' U') (R' F' R F) U2 F2 R
"U (R U' L' U R' U' L) (R U2' R2' F R F' R U2' R')
 U r' U (r' F R F') (r U2 R' U') (R U R' U) r"
(R U' R2' U2' R2 U R2' U) (F R F' R U R')
(R U2' R2' F R F') R U2' R'
(R' U2' R U R' U R) (f U R U' R' f')
U (L U2 L' U' L U' L') (f' U' L' U L f)
(f R U R' U' f') (R U R' U R U2' R')
(L' U' L U' L' U2 l2) (U F U' F' l' U M')
U (R U R' U R U2' r2') (U' F' U F r U' M')
U' (F R U' R' F' L' U L) U (R U R' U R U2' R')
U (R' F' R U') (F' U' F U') (R U' R' U') F
(R U R' U) (R U' R' U)2 (R' F R F') (R U2' R')
U (R U R' U) F' U F (r U' R' U') R U M U R'
(f R U R' U' f') U' (R' U2' R U R' U R)
U2 (R' U' F' U F R) U2 (R U2' R' U' R U' R')
U2 S' (R' F R U R' U' F' U R) S
U2 R' U' (R U' R' U') (R U2 R' U') (F' U F U) R
"U2 F' U2' L D (L' U' L D') (L2' U L U') F
U' (R' U' R' F R F' U R) U (L' U' L U L F' L' F)"
(R' F R U R' U' F' U R) (F R U R' U' F')
"U' (L U2 L' U' L U' L') U' (L' U' L U L F' L' F)
 U (R U2' R' U' R U' R') U' (F R U' R' U R U R' F')"
U2 (R U R' U' R' F' R U2 R U2' R' F2) (R U R' U' F')
(R U2' R2' U2')·R2' U R F (R U R U') F'
U2↑R2' D' (r U' r' D) (r U R U' M)
"U (M2' U M2' U2 M2' U M2') (F' L F L' U' L' U L)
U (R' F R U) (R' F' R U) F U' (F R' F' R) U' F'"
R' U (R U R' U2') (R U2 R' U2') (F' U F U) R
U2 F U2 (R' F' U' F U R2) U' R' U' F'
U' (R' U' R U') (R' U R U') (R' U R) (F R' F' U F R F')
U2 R' U2'↑R2' U2' F R F' (U2 f' U' f)
U F (R U' R' U) (F R U R' U' F') (R U R' F')
U (r' F' r2 U R' U') (r' F R2 U R' F')
U (F U2' F' U') (R' F R U' R' F' R)
U2 (R' U' r U) R' U' R2 D (r' U' r D') r' R' U R
(R U' R2' F R F') U (R U r' U' R U R'M')
"(L' U2 L U L' U L) U (L' U' L U L F' L' F)
 U2 (R' U2' R U R' U R) U (F R U' R' U R U R' F')"
(f R U R' U' f') (R U' L' U R' U' L)
(R U R2' F R F') (R U' R' U') (R U' R' U) F' U2 F
"U' (r U r' U R U' M' U' r') (R' U' F U R U' R' F' R)
F (U R U' R')2 F' U (R' F R U R' U' F' U R)"
"(L' U R U' L U R') (L' U2 L2 F' L' F L' U2 L)
 (L' U R U' L U R') U' (R U2' R2' F R F' R U2' R')"
U (L' U L2 U2 L2' U' L2 U') (F' L' F L' U' L)
U' S (L F' L' U' L U F U' L') S'
"U' L U (L' U L U) (L' U2' L U) (F U' F' U') L'
 U (R U R' U) (R U R' U2') R U y (R U' R' U') F'"
U' F U2 R' D' (R U R' D) (R2 U' R' U) F'
"U (L F' L' U' L U F U' L') (F' L' U' L U F)
U' (M' U M U') (r U r' F' U F r U' r')"
U2 (R' U2' R U R' U R) U (R U R' U' R' F R F')
"U' (L' U' L U L F L' U2' L' U2 L F2') (L' U' L U F)
 U' (R U' R' U) (R U R' U2) R U2' (f U R U' R' f') R'"
"U (L' U2 L2 U2)·L2 U' L' F' (L' U' L' U) F
U2↑R' F' (r U2' R' U) (r' F r U' r') F2 R2"
U R2 D (r' U r D') (r' U'·R' U M')
"(M2' U M2' U2 M2' U M2') (F R' F' R U R U' R')
(r U' r' U') (r U r' U') (R U' R' U) F' U2 F"
U' (R' F R U R' U' F' U R) f (U R U' R')2 f'
U2 R' U2' (F R U R' U' F2) U F U R
U2 (L U L' U) (L U' L' U) (L U' L') (F' L F U' F' L' F)
U2 F' (U' L' U2 L F) (R U R' U')2 R U' R'
U (R' U2' r U) (R' U' R U) R' U' (MR U R' U R)
U2 (r U R' U R U2') (M U R' U R U' R' U R U2' R')
U' M' F U' (R U' R' U) (r' F R F') M' F' M
F (R U R U) (R' U' R' U2') F R F' U R' U F'
U' (r U' r' U') (R U' R' F2) U F (R' F R)
U2 (R' F R U) (r' F r) (F2 U' F') (r U' r')
U (R' U2' R U) (R' U' r U) R' U' (MR U R' U R)
U2 R2' F2 r U' M F2' (R U2' R' U2) F R
U R' U' F' U' F (r' F R F') (r U' R' U') R
U (R' U2' R U R' U R) U' (r U R' U R U' R' U R U2' r')
U' (R U2' R' U' R U R' U' R U') (R2' F2 r U r' F R)
"(R U R' U') R' F (R2 U' R' U) (R U R' F')
U (L' U' L U L F' L' F) U2' (R U R' U' R' F R F')
 U' (F R U' R' U R U R' F') U' (R U R' U' R' F R F')"
U (r U2' R2' D') (R U' R' D) R2 U' r'
U2 (R' F' U' F U R2) (U R' U' R' F R F')
U' (F R' F' R U2 R U2' R') U2 (R' U' F' U F R)
(R' U R U) R2' F (R2 U R' U') F' U2 R
U (S R2' S') R U' (F R' F' R2) U F R F'
"(L U F U' F') (U F' U' L' U L F L')
U2 (R U R' U) (R' U' R U') (R' U2' F R F')"
"U' (L F' L' F) U (F' L F L2' U' L U2') (L F' L' F)
U (r U R' U' r' F R F') U' (F R' F' R U2 R U2' R')"
"↑ L U F (U' R U2 R')2 F' L'
U2 (R U R' F') U2 (R' U' R U' R' U2' R) U' (F R U' R')"
U' (L' U' L U) (L U F' L' F) (L U L' U' L U' L')
U (R U R' U) (R U R' U') (F' U2 F U) R U' R'
(R' U' F' U F R) U2 (r U R' U' r' F R F')
(R U2' r2' F R F' r U2' R') U' M'
"U2 (f' L' U' L U f) (l U L' U L U2 l')
U' (R' U' F' U F R) U (r U R' U R U2' r')"
U' (f R U R' U' f') (r' U' R U' R' U2' r)
U' (R U2' R2' U') F D' F D F U F R
U (r U R' U R U2' r') (R' U' F' U F R)
(l' U' L U' L' U2 l) (L U F U' F' L')
U (R U R' U R U2' R2') (U' F' U F R)
(R' U' R U' R' U2' R2) (U B U' B' R')
U' (R U2' R' U' R U' R2') (U' R' F R F' U R)
U2 (L' U2 L U L' U L2) (U L F' L' F U' L')
U' (R U' M' U') (R' U R U) (r' F' U' F) (U' R U' R')
(R' U2 R U) (R2' F R F') U R
"U (F' L F L') (U' L' U L)
F (R U' R' U') (R U R' F')"
"FS' (R U' R') (f R' F' R) U F'
(FS' R U' R' S) (U' R U R' F')
U2 (S L' U' L S')(F U' F' L' U L)"
U (R U R' F') U2 F U (R' U' F' U F R2) U' R'
U' R U2' R2' U' F' U F (R2 U R' U') R U' R'
U' (R U R' F') U (R U2' R' U2) (R' F R U) R U2' R'
U (R U2' R' U2) f' U' F U S
U F' L F U2 (L' U' L' U) L2 U2 L'
"U (F' L F L' U' L' U L') (U' L2' S' L2 S U L2')
 R' U R' U' F R F' R' U (R2 U R' U2') R"
"U (F' L F L' U' L' U L) (M2' U M2' U2 M2' U M2')
(F' L' U' L U) (l' U' l U L' U L U l' U' l F)
U' F' r' U' F' (R U' R' U2') r F (U' R U2' R')"
F U (R U' R2' D') (R U2 R' D) R U2 F'
U2 R' U' F (R U' R' U2') (R U R' F') R
U M' U' (L' U l U) F U' F'
(R U R' U') R' F (R2 U' R' U) (R U R' F')
U2 F (R U R' U2) (R' F R F') (R U R' F')
U2 (r' U2' R2 D) (R' U R D') R2' U r
U2 (F' L F L' U2' L' U2 L) U2' (L U F U' F' L')
U' (R U' R' F) (R' F' R F') U' F U R U R'
(S' L2 S) L' U (F' L F L2') U' F' L' F
U (R' U' F' U F) (U' F U R U' R' F' R)
U2 (R' F R F') U' (F R' F' R2 U R' U2) (R' F R F')
U↑R' U' F' (U L' U2' L)2 F R
U2 (R U R' U') (R' U' F R F') (R' U' R U R' U R)
(L' U' L U') (L' U' L U) (F U2' F' U') L' U L
U (R U2' R' U2 R' F R F') (R' U2' R U R' U R)
(F R' F' R) (U R U' R')
"U F'S (L' U L) (f' L F L') U' F
U (F' S L' U L S') (U L' U' L F)
U' (S' R U R' S)(F' U F R U' R')"
U' (R U R' U' R' F R F') U2 (R' U2' R U R' F' U F R)
r' D (R U R U) (R' U R U) (R' U R' D') r
U (f U R U' R' f') (R U2' R' U2 R' F R F')
U' (L' U2 L U2') f U F' U' S'
F R' F' U2' (R U R U') R2' U2' R
"(F R' F' R U R U' R) (U R2 S R2' S' U' R2)
 U2 F (R U R' U2') (R U' R' F') U' F (R U2 R' F')"
"(F R' F' R U R U' R') (M2' U M2' U2 M2' U M2')
U (F R U R' U') (r U r' U' R U' R' U' r U r' F')"
U F' U' (L' U L2 D) (L' U2' L D') L' U2' F
U2 (F R U R' F') U' (F' r U r')
M' U (R U' r' U') F' U F
(r U R' U R U2' r') U (R' U' R U' R' U2' R)
U2 (R U R') (U R U' R')2 (F' L' U2 L U F)
U (R' F' r U' r' F2) (U2' R U R' U R)
(L F l' U l F2') (U2 L' U' L U' L')
(F R' F' R) (U R' F' R) (U R U' R') (F R U' R')
U (F' L F L') (U' L F L') (U' L' U L) (F' L' U L)
U2 (R' U' F U R U' R' F' R2) (U2' R' U2 R' F R F')
U' (L U F' U' L' U L F L2') (U2 L U2' L F' L' F)
(L' U2 L U L' U L) (F U F2' L F L2' U L)
(R U2' R' U' R U' R') (F' U' F2 R' F' R2 U' R')
(R U R' U R U' R' U R U2 R') U (r' U2' R U R' U r)
U' (r' U' r U') R' U (r' F R F2) U F r
U2 (R U2' R' U2) (R' F R F') (r' U' F' U F r)
U' (↓F R U R' U' F') (R2 D R' U2 R D' R' U2 R')
"U (L' U2 L) (F R U' R' U' F') (U L' U2 L)
 (R' U' R U) (R U2' R' U') (R' U R U2) (R' F R F')"
"(F R' F' R U R U' R') U2' (F R' F' R U R U' R')
U (F' L' U L U L' U' L F2) (R' F' R U R U' R')"
U2 (L U2 L' U' L) (F' U' L' U L F L')
U' (R2 D R' U R D' R2') (U'· R' F R F')
U' (R U2' R2' F R U) R' U' F' U (R U2' R U' R')
U (F U R' U' F' U F R) (U R U' R' F')
F (L' U L F) (L F' L' F') U (L' U2 L F')
U (R U R' U R U' R' U R U2 R') (F R' F' R U R U' R')
U (R' F' R U) (R' U' R' F2) R F' U R
U2 (R U2' R' U2 R' F R F') (R B U B' U' R')
U (F R U R' U' F') (R U2' R' U' R U' R')
U2 (L F U F' U' L2') (U' L U' L' U2 L)
U (R' U' F' U F R) f (U R U' R')2 f'
U F (R U R' U')2 F' (R' U' F' U F R)
"(l U2 L' U' L U' M') (F U F' U' L')
 U (F R U' R' U2' R U2 R' U') (R U R' U' F')"
F U2 (r U r' U2) F' U' (R' F R F' R U R')
U F' U' r' F r2 U' r' F2 R U2 R'
U2 (R' F' U' F U R) (L' U' L U' L' U2 L)
U r U (M U R' U) (F' U' F U') r U' r'
U' (l' U' L U' L' U2 l) (f' U' L' U L f)
"U2' (L F U F') (L2' U' L2 U' L2' U L2 U' L2' U2 L)
 U2 F (R U R' F) (R' F' R U') (R U' R' U2') (R U R' F')"
U2 (r U R' U) (F' U F U') (R U' R' U) R U2 r'
U2 (F l' U' L U l F' L') U' (L' U' L U L F' L' F)
U R' F R2 U2' R' F' (R' F R U') (R U' R2' F') R
U (R U2' R' U' R U' R') (F R' F' R U R U' R')
"U2↑ l2 D (l' U l D' l') U (L' U' L U') l'
U' (F R' F' R U R U' R') U (r U2' R' U' R U' r')"
U (R U2 R' F) (R' F' R U) (R' F' U' F U R2) U R'
U2 (R' F' U' F R U') (↑R2' D' R U2' R' D R2)
U (r U' r' U r U) (R' U R U') (r' F' U F)
U' (R2 D R' U2 R D' R' U2 R') (F R U R' U' F')
U' (R U' R' F') U' F U (R U R2' D') (R U' R' D) R
U2↑R2' F2 R U' F (R' F R F') (↓R U R' F U' F U R)
(R' U' R U' R' U2' R2) (U R' U R U' R' U' R' F R F')
U' (↓r U2 R D) (R' U' R D') (r' U R' U') r U' r'
"U' (L' U2 L2 F' L' F) (L F' L' F) (L' U L U) (L F' L' F)
U' (R U2' R' U) F' (r U' r' F2) U (R' F R F')"
U' R' U F' (R' F' U' F U R) U' F U' R
(R U' R' U2') (R U R' U) (R' F R F') U (R' F R F')
U' R U R2' F2 r U' F' U F r' F2 R
U (F U R U2 R' U' R U R' F') U (R' U2' R U R' U R)
"U' (F' L' U L U' L' U2 L U) (L' U' L U)2 F
 U' F U (R U' R' U) (R U2 R' U) (R U R' U) (R U' R' F')"
R D (r' U r D') (R2' F' U' F R)
U (R' F R U R' U' F' U R) U (R U2' R' U' R U' R')
"U' (L U2 L' U' L U' L') U' (F' L F L' U' L' U L)
 U (R U2' R' U' R U' R') (F R U' R' U' R U R' F')"
U2 (L' U2 L U L' U L) U (L' U2 L U2' L F' L' F)
U (R' F R U R' U' F') (R U' R' U2' R)
(R' U2' R2 U) R2 F' U F R2 U' R'
U (f' U' f) (L f' L' U) (L f L')
"U2↑R' U (L F' L2' U' L U') (F' R' F2 R2)
(↑r' F R U') (R2' F' R F') (U' L' U2 L2x)"
S (R' F R f') (r U R' U' M)
U' F' U' F (R U2 R D) (r' U r D') R2
(r' F R F') (r U2 R' U') M' U R U' r'
U' (R' F R F') (R U' R' U) (R U R' U) F' U' F
U2 (F R' F' R) U2 (R U' R' U) (R' F R F) (r U r' F)
U' (R U2' R' U) (R U R' U2) (R U' R2' F R F') R U R'
"U' (L' U2 L U) (L' U' L U) (L' U' L U2') (L F' L' F)
U (R U R') (F' U' F) (R U R' U')2 (R U' R')"
U (R U' R') (F' U' F) (R U R' U) (R U' R' U') (R U R')
U F U (R U' R' U) R2 D (R' U' R D') R2' F'
U (R U R' U2') (R U' R' U') (R U2' R2' F R F') R U R'
"U' (L' U2 L U L' U L) F' (L' U' L U)2 F
(R U2' R2' F R) (F2 U F U2') R U' R'"
U' (r U M U R') (U' r U' r')
U' (R U' R' U) (M U r U') (r' U' r U) R'
U2 (R' U' R F) U (R U' R' U') (R' U R U) F'
U' F' U2 (R U R' U') R' F R2 U' R' F' U2' F
"U (L' U2 L2 F' L' F L' U2 L) (F' L' U' L U F)
U (r U' r' U') (R U2' R' U' R U' R') (U' r U r')"
U2 (R' U' F' U F R) (F U R U' R' F')
U (R U R' U R U2' R') U (r' U2' R U R' U r)
U (f' L' U' L U f) (L' U' L F U2 F' L' U L)
U' (r U' r' U2') (R U' R' U') r U' M U2 R'
U2 (R U R' U R U2' R') U' (r' U r2 U' r2 U' r2 U r')
"U2 (L U L' U L U2 L') F' (L' U' L U)2 F
U' (R' U2' R U R' U R) U' f (U R U' R')2 f'"
U(↓ F' L' U' L U F) (L2' D' L U2' L' D L U2' L)
U2 (R' F2 r U2' R U' r' F) (R B U B' U' R')
U' (R U2' R') (F' L' U L U F) (U' R U2' R')
"(F' L F L' U' L' U L) U2 (F' L F L' U' L' U L)
U' (F R U' R' U' R U R' F2') (L F L' U' L' U L)"
U2 (R' U2' R U R') (F U R U' R' F' R)
"U (L2' D' L U' L' D L2) (U· L F' L' F)
 U2 (R U R' U) (R U' R' U') F' U2' F U R U R'"
U' (R' U2' R2 U) (R' F' U' F U R) U2' (R' U2 R' U) R
"U' (F' U' L U F U' F' L') (U' L' U L F)
U2 R' U' (F U R U' R' F') U' F' U F R"
F' (R U' R' F') (R' F R F) U' (R U2' R' F)
U (R' U' R U' R' U2' R) U' (F R U' R' U R U2' R' U' F')
U2 R' U' (R F R' U) R (F R' F' R) U' F'
"U2 (L' U2 L U2' L F' L' F) (L' B' U' B U L)
U (F U R U2' R' U' R U R2') (F' r U R U' r')"
U' (F' L' U' L U F) (L' U2 L U L' U L)
U2 (R' F' U' F U R2) (U R' U R U2' R')
U' (L U F U' F' L') f' (U' L' U L)2 f
"U' F' (L' U' L U)2 F (L U F U' F' L')
U2 (R U2 R' U') (R U R' U) (F' U' F U') R U' R'"
(r' U2' R U R' U M') (F' U' F U R)
U2 R' F' U2' F U' (R U R2' F R F') (R U R' U R)
U' (F U R U' R' F') (R' F2 r U r' F R)
U2 (L F U F' U' L') (R U R' U R U2' R')
"U' l' U' (M U' L U') (F U F' U) l' U l
U' (R' U R U2) (R' U' R U2') (R' U' R U') (R' F' U F) R"
U (r U R' U R U2' r') (f U R U' R' f')
U2 (R' F' U' F) (R2 U R2' U R2 U' R2' U R2 U2' R')
r' U' (R U' R' U) (R' F R F') (R U' R' U2) r
U2 (F' r U R' U' r' F R) U (R U R' U' R' F R F')
U' R' (F' L' U' L U F) R2 D (R' U R D') R'
U' (L' U2 L U L' U L) (F' L F L' U' L' U L)
"U2↑r2' D' (r U' r' D r) U' (R U R' U) r
U (F' L F L' U' L' U L) U' (l' U2 L U L' U l)"
U2 (R U2' R2' F R F') (R' U' R U') (R' U2' F R F')
U2 (L F U F' L' U) (↑ L2 D L' U2 L D' L2')
F' U' F r U (R' U' R U') (r' U' r U r')
(R' F' R U) R' D (R U2 R' D') (R U R' U') F U R
U' F U R U' R D (R' U' R D') R2' U' (R U R' F')
U2↑ L2 F2' L' U F' (L F' L' F) (↓ L' U' L F' U F' U' L')
U' F R F' U2 (R' U R U) (R' U' R U2) F R' F'
U2 (R U2' R' U') (R U R' U2) (F' U2' F U) R U R'
U' (f U f') (R' f R U') (R' f' R)
U2 L U' (R' F R2 U R' U) (F L F2' L2')
S' (L F' L' f) (l' U' L U M)
U (R' F' U F) R' D' (r U' r' D) R2
U (F R' F' R) U (R' F' U' F U R2) U2' R'
U (L F' L' F) (L' U L U') (L' U' L U') F U F'
U (r U2' R' U') (R U R' U2) (r' F R2 U R' U') F'
U (R' U' R U) (R' U2' R U') R' U2 F' U2' F U' R
U (R U2' R' U') (R U R' U') (R U R' U2) (R' F R F')
U' (L' U L) (F U F') (L' U' L U') (L' U L U) (L' U' L)
U' R' U2' R F (R U R' F') R' F U' F' (R U' R' U') R
(R U' R' F) R' F' R2 U2' (R' U R U) (R' U2' R U') R'
U (R U2' R2' F R F') (R' F R F') (R U' R' U') (R' F R F')
F U' R (F R U R' U' F') U R' U F'
U2 (R U2' R2' U' R) F' (R' U R U) (F R U' R')
U' F' U2 F2 U (R U' R' F2) (L' U L F)
U' (R U R' F') (R U R' U') R' U' F R2 U' R2 U2' R
U (F R U' R' U R U2' R' U') (R U R' U')2 F'
L' D' (l U' l' D) (L2 F U F' L')
U' (L F' L' U' L U F U' L') U' (L' U2 L U L' U L)
U (R' U2' R U R' U R) U (F R' F' R U R U' R')
U2 (R U2' R' U' R U' R') U' (R U2' R' U2 R' F R F')
U' (L F' L' U' L U F) (L' U L U2 L')
U2 (R U2' R2' U') (R2 f R' f') R2' U R
U (R U2' R' U' R U' R') F (R U R' U')2 F'
U' (r' U' M' U' R) (U r' U r)
U' (R' U R U') (M' U' r' U) (r U r' U') R
U2 (L U L' F') U' (L' U L U) (L U' L' U') F
U2 F' U' F (R U2' R' U2) (R U R' U) F' U F
U' (R U2' R2' F R F' R U2' R') (F R U R' U' F')
U' (L' U' L U' L' U2 L) U' (l U2 L' U' L U' l')
U (F U R U' R' F') (R' U' F' U F R)
U' (f R U R' U' f') (R U R' F' U2' F R U' R')
U2 (r' u' R U') (R U R' u) (r U' R U' R')
U (r U r' U2) (R U2' R' U2) (R U R' U') r U' r'
U2 (R' U' R U' R' U2' R) F (R U R' U')2 F'
U' F (R U' R' U2) R U R2' (F' U' F U) R U' F'
U2 (F' L' U' L U F) (L F' L' U' L U F U' L')
U2 (R' U' R U) (R' U R U) (R' F' U' F U' R)
r' U' (R U' R2 D') (R U2 R' D) R r
U (F R' F' R U2 R U2') (R2 U2' R U R' U R)
U' (R U R2' F R F') U F R' F' U2' (R U R' U R)
U (F R' F' R U2 R U2' R') U (R U R' U R U2' R')
(L F U' F') (L2' D' l U l' D L)
U' (R U R' U') R U' F U F' R2' F R U' F'
U' F (R' F R U2) (r U' r' U2) F r U r'
"U2 (r U R' U' r' F R F') (r U2' R' U' R U' r')
U F (R U' R' U) (r' F R F') (r U' R' U') F'"
U (L U2 L' U2') (L U L' U2) (L F' L F L2') (U' L U' L')
"(L' U2 L2 F' L' F L' U2 L2) (U2 L' U' L U' L')
U' (R U2' R2' F R F' R U2' R') U (R U2' R' U' R U' R')"
U' (L U2 L2' U' L2 U' L2' U2 L2) (U F U' F' L')
U2 (R' F' R U') F U2 (R U R' U) F' U R' F R
U2 F' U' (L F' L' F)2 (L' U L F)
U' (F' U' F U) (R U' R' U) (R U R' U) F' U' F
U (F R U R' U' F') (r U M U R' U' r U' r')
"U' (L' U2 L) (F' L F L') U (L' U' L U) (L' U L)
U (R' U2' R U R' U) (F' U' F U' R U R' U R)"
r' U' (F' U F U') (R U' R' U2') r
U2 (R U2' R' U' R U' R') U' (↑ R' U' R' F R F' U R)
U2 (R U2' R' U' R U' R') (F U F R' F' R U' F')
U' F (U R U' R')2 F' U (f U R U' R' f')
(R' U' F' U F R) (r' U' R U' R' U2' r)
"U' (l U L' U L U2) (F' L' F l' U' L)
 F (R U R' U) F' U' (R' F R U' R' F' R)"
U (r U' r' U' r U r' F' U F) (r U R' U R U2' r')
U2 (R' F' U' F U) (R2 U2' R' U2) (R' F R F')
U' (F' L F L' U' L' U L) (R U2' R2' F R F' R U2' R')
"U (↑ L2 D L' U2' L D' L2') (U' L F U' F' L')
 U' (R U R' U') F' U' F (R' U' R2 U' R2' U2' R2 U R')"
U (R U' R' U') F' U2' F U2 (R U' R' U) R U2' R'
U2 (R' U' R U) (R' U' R U2) (R' U' R U') (R' F R' F' R2)
(R' U' F' U F R) U2 (R U2' R' U2 R' F R F')
U' (R U' R' U2) (R' F R U) F' (R' F R U') F2 U F
"U (l' U2 l) (F' L F L') (l' U' l) (F' L F L')
 U' F U (R U' R' U') (R U' R' U') (R' F R F') U2 F'"
"U2 (L' U2 L2 F' L' F) (L F' L' F) U2 (L F' L' F)
 F (R U R' F) (R' F' R U') (R U' R' U) (R U R' F')"
"(R' U' R U' R' U2' R) (L F' L' U' L U F U' L')
 (R' F U' F' U) R U F U (R U' R' U') F'"
U (F U R U2' R' U R U R') (U R U' R' F')
U2 (R U R' U') (R' F R2 U' R' U) (R U2' R' U') F'
U' (l F' L' F) (l' U L U) (L' U' L U2') (L F' L' F)
↑ L U2' (L' U L U) (l F' L' F) (L' U L U') l'
U2↑R2' D' (r U r' F) (r U r' F2) D R2
"f' U' (L' U L2' F) (L' U' L' U L) S
U (R' F' U' F U) (r' D' r U' r' D r U R)"
U2 f U2 (r U r' U2) f' (R U R' U') F' U' F
U2 (R' F' U' F U R) (F' L F L' U2' L' U2 L)
"U2 (L' U' L U L F' L' F) U2' (L' U' L U L F' L' F)
U2 (L' U' L U L F' L' F2) (R U' R' U R U R' F')
U R' F U2 F' (R F R' U2') (R U R U') R' F'"
U2 (↓R U R' U') R U' (F U R U' R' F') (R' U R U' R')
U2 (l' U' L U' L' U2 l) (F' L F l' U' L' U l)
U2 (L' U' B' U B L) (F' L F L' U2' L' U2 L)
"U (F' U' F) (L' U2 L2 F' L2' U2 L U) (L F L')
U (r U R' U2) (r' F R U) (R U' R' F') r U r'"
(r' F R F') (r U r' U) (M' U2 M U M')
↑r' U2 (R' F' R U R U' R' F) U2' r
U'↑R' U' (R U' R' U) (R U' R') (f U R U' R' f') U' R
R' F' U2' F (R U R' U') (R U2' R' U2) (R U2' R' U2) R
(R U R' U) (R U' R2' F R F' R) U (R' F' U F)
(R U2' R' U') (R U R' U2) (R' U' F R F') (U' R' U2' R)
U2 (R U' R' U) (F' U' F U2) (R U R' U) R U R'
U2 (L' U' L U L F' L' F) (R U R' U' R' F R F')
U2 R2' D' (r U r' D) (R F' U' F R)
"U2 (L' U' L U') (L F' L' U' L U F U' L') (U L' U2 L)
U2 (R U2 R' U') (R U R' U') (R' F' U' F U R2) U2' R'"
U2 F' U' (r U r' U') (L' U L U) (r U' R' U) R U r'
U2 (R B U B' U' R') (F U R U' R' F')
U2 M'(R' U' R U' R' U2 R U' R) r'
U (R' F R2 B' R2' F' R2 B R') U' (R U R' U R U2' R')
U F' (L' U L2 U2 L2' U' L2 U' L' U) F
U (f U R U' R' f') (R' F' U' F U R)
U2 S (R' U' R U' R' U2' R U2) S'
(R' U' F' U F R2) (U2' R' F R' F' R U' R U' R')
U (r U R' U R U2 r') U (R' U2' R U R' U R)
"U (↑R' U2 R U R') (F R' F' R)2 U R
U' R U2' R2' F2 (r U' R U') R' U2 r' F2 R"
(R U R' U R U2' R') (r' U r2 U' r2 U' r2 U r')
(R U R' F' U2 F R U' R') (f U R U' R' f')
(R U' R' U') (R U R' U') r (R U R' U R U2' R') r'
U' (R U' R' U) R U (F R U R' U' F') (R' U2' R U2) R'
U2 (F R U R' U' F') (R' F R U R' U' F' U R)
U2 (L U L' U') (L U' L' U') (L F U F' U L')
U2 (r U R' U) R2 D (R' U2 R D') R' r'
U R U R2' F' U' F R2 U' R2' U F' U F R
U' (R' F R U) (r' F R F') r U' R2 F' (R U' R U') R'
(R' F' U F) (R2 D r' U' r D' R')
U' (F' L F L' U2' L' U2 L) U' (L' U' L U' L' U2 L)
U (L' U R U' L U R') F (R U R' U')2 F'
R2 D' F2 (r U' r' F') (r U' r' D) R2
"U2 (l' U' L U l F' L' F) (l' U2 L U L' U l)
(↓F R F' r U R' U' r2') (U2' R U R' U r)"
"U' (R' U2' R U2) (R' U' R U2') (R' F R' F' R2) (U R' U R)
 U2 (R' U2' R U) F (R2 U' R' U) R U R F'"
(R U2' R2' F R F' R U2' R2') (U2' R U R' U R)
U (R' U2' R2 U R2' U R2 U2' R2') (U' F' U F R)
U' (R' F R F' r U R') U' (R U2' R' U2) (r' F R F')
U2 F U (R' F R F')2 (R U' R' F')
U' (f U R U' R' f') U' (r U r' U R U' M' U' r')
U2 (r U R' U) (R' F R F') R U2' r'
U2 (r U2 R' U') (R U R' U) (F' U' F U') R U' r'
U (R U2' R') (F R' F' R) U' (R U R' U') (R U' R')
"U2 (L' U2 L U L' U L) U (↑ L U L F' L' F U' L')
 U' F (U R U' R')2 F' U' (F U R U' R' F')"
U2 (L' U2 L U L' U L) (F' U' F' L F L' U F)
U F (R U R' U')2 F' (R U B U' B' R')
"(L U F U' F' L') (l U L' U L U2 l')
 U' F U (R U' R' U) (R U2' R' U2) (R U R' F')"
U (r' U' R U' R' U2') (F R F' r U R')
U (R U2 R' F) R' U' R2 U' R2 U F' U R
U' R U' R2 U2' R2 U (R2' F R F' R') U R2 U R'
U' (R U2' R' U2) (R' F R U) R' U' R F' U' R' U2' R
U' (R2' D' R U2 R' D R2) (U R' F' U F R)
U2 (r U r' U) R U' r D (R' U R D') R' U2 r'
U' (r' F R U) R' F U' F' (R U' R' U2') R U2 M'
U' F (R U2' R2' F R F') U (R U R' U') (R U' R' U') F'
R' U' (F U R U' R' F) (r U r' F) U' F' U F R
U' (r U2' r') (F R' F' R) (r U r') (F R' F' R)
U2 (R U2' R2' F R F') (R' F R F') U2' (R' F R F')
"(L U L' U L U2 L') (R' F R U R' U' F' U R)
 U2 (R U R' U R U2' R') U2 (R' F R U R' U' F' U R)"
U' (F U F') (R U2' R2' F R2 U2' R' U') (R' F' R) 
U' (R' U2' R U2) F (R U R' U') R' U R2 U' R' F'
"↑ l U2' (L F L' U' L' U L F') U2 l'
(r U r' F') (r U R' U') (r' F r U) R U2' r'"
U' R U R2' (F' U' F U) (R U2 R' F) (R2 U R' U') F'
U' (R' F R F') U' (F R' F' R2 U R' U') R U' R'
U2 (R' U' R' F') U F U R' U' R2 U' F' U2' F R'
U2 (R U R U) F R F' U2 (R' U' r U) R' U' r'
U (R U' R' U') (R U' R' U2) (F' U F U') R U R'
U2 (R U R' U' R' F R F') (L' U' L U L F' L' F)
R2 D (r' U' r D') R' U2' (R' F' U F)
U2 (R U R' U) (R' F R U R' U' F' U R) (U' R U2' R')
U2 (F R2 D R' U R D' R2' U') (R U R' U' F')
"U' (F' U' L' U2 L U' L' U' L) (U' L' U L F)
U (R U B' R B R2') (F' U F U) R U2' R'"
(R' U R U2') R2' U' F' U F (R U' R U) R' U R
U (r' F R F') (r U' R' U') (R U R' U2) (R' F R F')
U r' D' (R U R' D) (R2 U R' U') M' U' R U R'
U' F U' (R U R' U') (R U2 R' U') (R U2 R' U) F'
U2 (L F U F' U' L') (F R' F' R U2 R U2' R')
f U (R U' R2 F') (R U R U' R') S'
↑R' U2 (R U' R' U') (r' F R F') (R U' R' U) r
"U2 (R U R' U' R' F R F') U2 (R U R' U' R' F R F')
U2 (R U R' U' R' F R F2') (L' U L U' L' U' L F)
U2 (R U2' R' U) (R' F R F) (r U r' F) R U R'"
"U2 (↓ L' U' L U) L' U (F' U' L' U L F) (L U' L' U L)
U (F U R U2' R' U' R U R' F') (R U2' R2' F R F' R U2' R')"
U2 (r U R' U R U2' r') (F R' F' r U R U' r')
"U2 (R U B U' B' R') (F R' F' R U2 R U2' R')
U' (R U2' R' U2 R' F R F') U (R' U' R U' R' U2' R)"
(R' F' U' F U R) U' (R' F' U' F U R)
M(R U R' U R U2' R') U M'
(R' U' R U' R' U2' R) U' f (U R U' R')2 f'
U' F (R U' R2' U2' R2 U R2' U R U') F'
(R' F' U' F U R) (f U R U' R' f')
U2 S' U2 (R U R' U R U2' R') S
"(L U F U' F' L2') (U2 L F' L F L' U L' U L)
(R U R' F') U' (R U R' U') (R' U' F) (R2 U' R2' U2' R)"
U' (l' U' L U' L' U2' l) U' (L U2 L' U' L U' L')
U' (↑ L U2' L' U' L) (F' L F L')2 U' L'
U2 (r U R' U' M U R U' R') U (R' U2' R U R' U R)
(L' U' L F U2' F' L' U L) (f' U' L' U L f)
U' (F U' R' U R U F' R' U2' R) (F R U R' U' F')
"U (L U L' F') U (L U2 F' L' F) (L' U' L F)
(R U R' U') M' U (R U R' U2') (r' F R F')"
U' F' U F (R U' R2' F R F' R) U (R' U R U' R')
"(F' L F L' U' L' U2) (R U' L U R')
F' U' r' F2 R F' (r U R' U') F"
U F U' (R U2 R' F') U' F U (R U R' U) F'
U (R' F' R U) (R' F' U' F U R) U2 R' F R
"F' (L U L' U L U2 L') (U' L' U2 L) F
 U2 (R U R' F') U (R U2' R' U' R U' R') (F R U' R')"
(R U2' R' U2) (R' F R F')
U2↑r' U' (R U R') (F R' F' r) U (R U R' U2' R)
"U' (R B U B' U' R') (F R' F' R U R U' R')
(F U R U2 R' U' R U2 R' U') (R U R' U' F')"
"U (L' U' L U' L' U2 L) U (L U F' U' L' U L F L')
 U' (R' U' R U' R' U2 R) U (R U2' R' U' F' U F R U' R')"
U F U' R U' (F U R U' R' F') R' U F'
U' F (R' F' U' F U R2) U' (R' U R U') R' F'
U' (L' U' L U' L' U2 L) (F' U' L' U L F)
U2 (R U2' R' U' R U' R') U2 (R' F' U' F U R)
"U2 (l' U' L U') (l F' L' F) (L' U2 L) (M' U' M)
U' (M' U' M)(R U2' R') (F R' F' r) (U' R U' r')"
U L' U2 L (F' L F L2' U L U') L' U2 L
U (f R U R' U' f') (R U2' R' U' R U' R')
"U2 R U2' R' (F R' F' R) (U' R U' R')
(L U2 L' U' L U') (F U F' U' L')"
U (R U2' R' U) F' U' F R' U' (R2 U' R' U) R' U R
"U' (l' U' L U' L' U2 l) (F' U' L' U L F)
 U (r' U' R U' R' U2' r) U (R' U' F' U F R)"
U (R B U B' U' R') f (U R U' R')2 f'
U' (S U2 R' U' R U' R' U2 R U S') (R' U' F' U F R)
U2 F (R U R') (F R' F' R)2 U' F'
U2 F (R U R' U2) (R U R' U') F' U' F (R U R' U2) F'
U' (R' F R2 U R' U') (R U R' F') (R' F R U') F'
"U2 (L U2 L' U' L U' L2') (U' L U L F' L' F)
(R U2' R' U' R U' R') (F R U' R' U R U R' F')"
"U' (F' L F L' U2' L' U2 L2) (U F U' F' L')
 U (r U' r' U) (R U R' U) (r U' r') F' U F"
"U2' L U2 (L F' L' F) (L' U2 L U2) (F' L F L2')
U' F R' F' U2' (R U R' U) (R2 U' R' U) R U2' R'"
(l' U' L U l F' L' F) (l' U' L U' L' U2 l)
U2 (L F U F' U' L') (F' U' L' U2 L U L' U' L F)
U' (F R' F' R U R U' R') U (R U2' R' U' R U' R')
(r U M U R' U' r U' r') (R' U' F U R U' R' F' R)
U2 (↑R' U' R U2' R') F' U' (R U2' R' U' R U' R') F U' R
(R U2 R D) R' U2' R D' (R2 U' R' U') F' U F R
U R D (R' U' R D') R2' U' (R' U' F' U F R) U R
(↑ L2 F' L' F) (L' U' L U') (L' U2 L U') (L' U L U' L')
"(F' L F L' U' L' U L) U (L U2 L' U' L U' L')
F' U' (R' F R2 U R') E'U' (R' F R D')"
U (L' U' L U L F' L' F) (L' U' B' U B L)
"U2 (F' L' U' L U) (L F U F' U' L' U F)
U (R' F' U' F) U (F R U R' U' F') U R"
"U2 (l' U' L U') L2' D' (L U2' L' D) L l
 U (R' U R U2) R' (F R' F' R2 U R' U) (R U' R' U) R"
F' U' (L' U L2 F) (l' U' L' U l)
(R U2' R' U) (F' U' L' U' L F) (R U2' R')
(F' L F L') (U2' L' U2 L)
"U2 (L U F' L F L' U' L') U2 (F' L F L' U' L' U L)
U2 (R' U R U) (R' U2' R U) R' U2 (R' F R F') U2 R"
(R U2' R') (F' L' U' L F) (U' R U' R')
(f R U R' U' f') (F' L F L' U' L' U L)
U (r' F' U F) (r U' r' U2) F U r F U' F'
(R U R' U') (R' U2' R U) (R' F' U F) R2 U' R'
(L' U l U) (L' U' L M') F U' F'
U (R U2' R' U2) (F' U2' F U) R U R'
U R U2' R2' U' F' U F R U' (R' F R F')
U (M' U M U2) (R' F R F' r U r')
U (R U2' R' U') F' U F (R U R' U')2 R U' R'
F (R U' R' U') R U R2' F' (R U R U) (R' U' R U') R'
U F' U' F (R U R' U) (r U R' U') M
R' D (R' U' R UD') R U' F R F'
(R' F R F') M U R U' M' U (r' U' r U) R'
U2 F (R U' R' U') (R U2 R' F') U' F' r U r'
U' (F U R' D' R U' R' D R2 U R' U') (R U R' U' F')
U' (F' L F L' U' L' U L) (F R' F' R U R U' R')
l' U' L U' L' U2 l
"(L' U' L U') (L' U L U) (M' U' L' U l)
 U' (r U R' U') M U (R U R' U') R U' R'"
"(L' U' B' U B L) (F' U' L' U L F)
(R' U2' R U R' U) (F2 r U r' F R)"
F U (R' U' R2 U' R2' U2' R2 U R') F'
U2 (r' U r U') (R' U' R U' R' U2 R) U' r' U' r
U' (L U L F' L' F U' L') U' (F' L' U' L U F)
(S L' U' L S') (U' L' U2 L)
U' r' U' F U (r U r U') r' F2 U2 F'
"U (f' L' U' L U f) (L' U' B' U B L)
(R' F' U' F U R) U' (R' U' F' U F R)"
(l' U' l U') (L' U M' U l)
(F' L' U' L U) (L' U' L d' L U L' U L)
U' F (R U R' F) (R' F' R U') F'
U F U (R U2' R' U') (R U R2' F') (R U R U' R')
U' (R' U' R F) U' (R' U2' F R F') (R U R' F')
(F R' F' R U R U2') (L' U R' U' L)
U2 R' U (S U R U' R' f') U F U' R
U2 F (R U' R' F) (R U R' U') F' U (R U R' F')
F (R' U' R U' R' U2' R) (U R U2' R') F'
(L' U2 L U2') (L F' L' F)
"U2↑ l U (L' U' L) (F' L F l') U' (L' U' L U2 L')
U' F (R U' R' U')2 (F U R U' R' F') U' F'"
"U (L' B' U' B U L) (F' L F L' U' L' U L)
U2 F (R U' R' U) (R U R' U) (R' F R F') U' F'"
U' (R U R' U R U2' R') U' (R' U' F U R U' R' F' R)
U2 R' U F' U (R' U' F' U F R) F U' R
U (R' U' R U') (R U R2' F' U F) R2 U' R'
U (R U R' U R U2' R') (F U R U' R' F')
(R' U2' R U R' U R) U (f U R U' R' f')
U2 (r U R' U) (r' F R F') (R U2' R')(M' U M)
"U2 L' U2 L (F' L F L') (U L' U L)
 (R' U2' R U R' U) (F' U' F U R)"
U' (f' L' U' L U f) (L' U2 L U L' U L)
U' R U2' R' (F R' F' R2 U' R' U) R U2' R'
U (r U R' U R U2' r') (F U R U' R' F')
U (R U R' U2) F' U (R' F R2 U2' R' F') U2 R' F R
U (R' U' F R' F' R U R) U (R U R' U R U2' R')
U F U' (R U R' U) (R U' R' U') (R U' R' U2) F'
U2 F' (L' U' L) (F' L F L')2 U F
U2 (R U2' R2' F R F') (R U' R' U)2 R U2' R'
"U (L F' L2' U' L U) (L' U' L F) (L F' L' U) F
(F R' F2 U2' R) U (R U' R' U) (F R' U R)"
U2 (R' U2' R U R' U R2) (U R' U' R' F R F')
(r U R' U' r' F R F') (r U R' U R U2' r')
U (F R' F' R U2 R U2' R2') (U' F' U F R)
U2↑R' U2' (R' F R F') (R U2' R' U2') (F R' F' R2)
U2 (R' F' U' F U R) (F U R U2' R' U' R U R' F')
U (R' U2' R U R' U r) U' (r' F R U F R U' R' F')
U (F' L F L' U' L' U L) U (R' U2' R U R' U R)
(R U R' U2') R U2 y (R U R' U) (R U R' U) F'
U (L2' D' L U2' L' D L U2' L) (F' L' U' L U F)
R2' U' R U F (R U R' U') (R' F2 U F) R U' R
(↑R2' F R F') (R U R' U) (R U2' R' U) (R U' R' U R)
(R U' r' U') (R U R'M') F' U F
U2 R S (R U R' U') (R' F R f' R')
(R U' R' U') (F' U2' F U2) R U2' R'
U' (M' U' M U2) (r U' r') (F R' F' R)
U2 (R U R' U') (R' F R2 U' R' U') (R U B' R B R2') F'
U R' U (f R U R' U' f') (R U R' U') (R U R' U R)
"U' F U F' (L' U' L U') (l' U' L U) M
U2 (R U R' F') U2 (R U R' U') (R' F R U) R U2' R'"
U' M' U (r U' r' F) U' M U R' F' R
F' U' (r' F r2 U R' U2) (r' F r U') r' F2 R
U' F U' (R' U' F R F') R' U (R2 U R' F')
U (R U2' R' U') (R U R' U2) (R' F R2 U R' U') F'
U (F R' F' R U R U' R') (F' L F L' U' L' U L)
"(F R' F' R U R U' R') U' (R' U2' R U R' U R)
(R' B' R U' R' B R) (r U B U' r')"
U' (R U R' U' R' F R F') (R U B U' B' R')
U2 (F R U R' U') (R' F' U' F U R U' F')
(F R' F' R) U (R' U' R2 U' R2' U2' R2 U2' R')
F U (R U' R2' F') (r U R U' r')
(F R' F' R) (U2 R U2' R')
"(L' U2 L U') (F U R U R' F') (L' U2 L)
 (F R' F' R) U2 (R' U' R U) (R U2' R' U') R' U R"
"U2 (R' U' F R' F' R U R) U2' (F R' F' R U R U' R')
R' F2 U' (R' F2 R U) (F R U' R' F R)"
(L' U2 L) (F R U R' F') (U L' U L)
(f' L' U' L U f) (F R' F' R U R U' R')
U2 r' D (R2 U' R' U') (R U' R' U) (R U' R2' D') r
U (R' F R F') U2 (R U' R' U)2 F' U2' F
r U R' U R U2' r'
(R U R' U) (R U' R' U') (M' U R U' r')
(R U B U' B' R') (F U R U' R' F')
F' U' (L U L2' U L2 U2 L2' U' L) F
U (↑R' U' R' F R F' U R) U (F R U R' U' F')
(S' R U R' S) (U R U2' R')
U2 r U (MR U R' U) (r U2 R' U) r'
U2 F (R U' R' F') r2 F r U' F r
U' (f R U R' U' f') (R U B U' B' R')
(r U r' U) (R U' M' U' r')
(F R U R' U') (R U R' d R' U' R U' R')
F U (R' F R F') (R U' R' F')
U' (R' U' R U' R' U2' R) U (R U R' U' R' F R F')
(r U R' U' r' F R F') U2 (F U R U' R' F')
"U' (↑R2' F2 L F L' F R2') (B U2' B')
U' (r U2' R' U') (F' r U R' U' r' F R2) U' r'"
"U2 (F' U' L' U2 L U L' U' L) (U' L' U L F)
U2 (R U2 R' U') (R U R' U') (F' U' F U) R U2 R'"
U' (R U R' U) (R U R2' U') F' U F (R U R' F R F')
U (R U' R2' U') R F (R2 U' R' U) R U R F' R U R'
U' r' D (R2 U R' U') (R U' R2' D') r
"U' (L' U' L U) (L' U' L) (F U F' U2) (L' U L)
U2 (R U2' R' U2) (R' F R2 U' R' U2') (R U R' F')"
(R U R' U' R' F R F') U2 (R' U' R' F R F' U R)
"U2 L F2' (L' U2' L' U2) (L F L F) L2' U2 L
U2 (r U R' U' r' F R F') U (l' U' L U' L' U2 l)"
(F' R U R' U' R' F R) (U' F' U F) (R' F R F')
U2 (R U2' R' U2 R' F R F') (L U F U' F' L')
"U2 (l' U' L U') (l F' L' F) (l' U2 L U') M
 U' (M' U' R U2' r') (F R' F' r) U' R U' r'"
U' F U2 (R U R' U) (R U R' U') (R U' R' U) F'
U (L' U R U' L U R') (F R' F' R U R U' R')
"(L' U2 L2 F' L' F L' U2 L) (l U2 L' U' L U' l')
 U' (R U2' R2' F R F' R U2 R') U (r U2' R' U' R U' r')"
"U' (L' U' L U' L' U2 L) (f' U' L' U L f)
 U (R' U' R U' R' U2' R) U' (R' F' U' F U R)"
U2 (R U2' R' U' R U' R') (L U F U' F' L')
U' f' (L' U' L U)2 f (L F U F' U' L')
"U' (L' U' L U' L' U2 L) (F R U R' U' F')
 U (R' U' R U' R' U2' R) (f U R U' R' f')"
U2 r U2' (R' F R' F') (R U' R U') r'
"(L U2 L' U' L U' L') U (L U F' L F L' U' L')
U' R' D R2 U' (F U R U' R' F') R2' D' R"
(R' U' R U' R' U2 R2) (U2' R' F R' F' R2 U2' R')
U' (R U R' U) r' U' R2 U' R2 U (R' F R F') U r
U' F U' R2 D (R' U' R D') R2' U F'
U (R2 U R2' U) (R U2 R' U2') F U R U' F' R'
U (L' U' L U' L' U2 L) U (L' U' L U L F' L' F)
U2 (F R' F' R U R U' R') U' (l' U' L U l F' L' F)
U (R U' r' F R' F') (U2 R U R' U r)
U2 (R U R' U) (R' F R F') U2 (R' F R2 U R' U') F'
"U2 L U2 (L' U' L U) (L2' U' L U) (L U2 F' L' F)
U' (R2' F R F') U2 (R U2 R' F) (R' F' R U2 R)"
"(R' U' R U' R' U2' R) U (F R' F' R U R U' R')
 (R' U' R U' R' U2') (R2 U R' F' U F R U' R')"
U' F (R U R2' U') R2 U' R' F' (L' U L U) R' U R
U' (F R U R' U') (R' F2 r U' r' F2 R2 U2' R')
U' F (R U' R' U) R2 D (R' U R D') R' U R' U' F'
U2 (F R U' R' U R U2' R' U' F') U' (F U R U' R' F')
U2 r D' R2' U' (R U' R' U) R2 D r'
U' F (R U' R' U) (R U2' R' U') F'
U' F (R U2' R' U') (R' U2' R U R' U R) F'
U (R U R' U R U2') (R2' U2' R U' R' F' U F U' R)
U F (R U' R' U') (F R U R' U' F') (R U2 R' U') F'
U (r' U r' F2) R F' U' (R U' R' U2) R' F2 r2
U' M' U' (R U R' F') (R U2' R' U2) R' F R2 U' r'
U F U (R' F R F') (R' U' R F') R' U R
U' (↑ B' U2' B) (L2 F R' F R F2' L2')
U' f (R U' R' U) S' (R U2' R' U') F'
U' (↓ L' U2' L' D' L U2' L' D L2) (F' U' L' U L F)
U' F (R U' R' U') (F U R U' R' F') (R U R' F')
(R' F R F') (r U r' U2) M' U M
U2 (R' F R F') U' (r' D' r U r' D r)
U2 (R' F R U R' F' R F U' F2') (L' U' L U F)
U↑ l U2' (F L' U' L U L F' L') U2 l'
U2 (R' F R U) F U' (R U R' U') (R' F' R) (U2 L F2' L')
"(R' f R U) (R' f' R) (f U' f')
 U2 (L' U R U' L U R') U' (F U R U' R' F')"
(R U' R2' U) (R U2' R2' F R F') (R' U R' U' R2)
(R' U R U2') (R2' U' F' U F) (R2 U' R' U2 R)
U' F (R U2' R' U2) (R U R' U2') (R U R' U) F'
"U2 (L' U L U) (L' U' L2 U F U' F' L2' U' L)
U (F' R U R' U' R' F R) U' (F' U' F U R U R')"
U' R' U (R U R' U) (F' U F) (R' U' R2 U') R2' U2' R2
U' (L' U L U') (L' U' L U) (L' U L) (F U' F') (L' U' L)
U' (L F' L F L2') U f' L f
U' r U2' R' U' R U' r'
U' r U2' R2' U' (R2 U' r' U) R' U R
U' (R U R' U') M' U (R U R' U') R U' r'
U' S (R U2' R' U' R U' R') U' S'
U' (F' U' F U') (R U R' U') F' U2' F R U R'
"L F U2 (L' U' L U' L' U2' L) F' L'
U' (F R U R' U') (R U' R' U2 R U R' F')"
U2 (R B U B' U' R') (f U R U' R' f')
(R' F' U' F U R) (F R U R' U' F')
"U2↑ L U (L F' L' F)2 (L' U L U2' L')
U2 r U2' R2' U' (R U' r' U2') (R U2 R U2' R')"
U (F U R U' R' F') (R U B U' B' R')
U (F U R U' R') (U R' F R F' U' F')
U (L U L' U L U2 L') U' (L' U' L U L F' L' F)
U F R2 D (R' U' R D') R2' U' (R U R' F')
U' r D' (R2' U' R U) (R' U R2) D r'
U (R U R' U') R (F R U R' U' F') U (R' U R U') R'
U (↑ L2 F2' R' F' R F' L2) (B' U2 B)
R' U F' U F (R U R' U) L' U R U' L
U2 (F U R U2' R' U' R U R') (U R U' R' F')
U (R U R' U') (R U R') (F' U' F U2') (R U' R')
U2 R' F2 (R U2 R U2') (R' F' R' F') R2 U2' R'
"(L' U' L U L F' L' F) U2' (L U L F' L' F U' L')
U' R' U2' (F R' F' R) U2 R U' (R' U2' R U') R' U' R"
U2 F (R U' R' U') R U R2' F2 (R U2 R U2') R' F
U2 (L' U2 L U2' L F' L' F) (R' U' F' U F R)
U2 (r U R' U) (r' F R F') (r U2' R' U) M
U' (R U' L' U R' U' L) (F' L F L' U' L' U L)
U2 (R' F' U' F U R) (S U' R' U2' R U R' U R U2 S')
(R U2' R2' F R F' R U2' R') (r' U2' R U R' U r)
U (R U R' U R U2' R') (f U R U' R' f')
"U2 (L' U2 L U L' U L) (R' U' F' U F R)
(R' U2' R U R' U R) U2 (R' U' F' U F R)"
U f (R U R' U')2 f' (R' F' U' F U R)
U (R U R' U R U2' R') (F' L' U' L U F)
(r' U2' R U R' U) (F' U' F U r)
(R' U2' R U R' U R) U' (R' U' F R' F' R U R)
(L U L' U L U2' L2') (U2 L F' L F L2' U2 L)
U2 r U (M U R' U2') F (R U R' F) (r U r2' F r)
U F U' R2 D (R' U R D') R2' U F'
U2 (R U2' R' U) (R U' R' U') (R U2' R2' F R F') R U R'
U' (R U R' U R U2' R') U' (R U R' U' R' F R F')
U2 (F' L F L' U' L' U L) U (r U R' U' r' F R F')
"U' (L' U l F' L F) (U2' L' U' L U' l')
 U (R' F R U) (R' F' R U) F U' (R U' R' F')"
U2 (R U2 R' U') F' U' F (R U R' U')2 R U' R'
U2 R' U2' (R U R' U') (R2 U R' U') (R' U2' F R F')
"(L U L' U L U2 L') U' (F' L F L' U' L' U L)
 U2 (R U R' U R U2' R') (F R U' R' U' R U R' F')"
U M' U M (R U R' U R U2' R2') F R U F U' F'
(R U2' R2' F2) (r U r' F2) (R U R U') R' F'
U R' D' (R U R' D) (R2 U' R' U') F' U F R U R'
"U2 (F' L' U L U' L' U2 L U F) U (F' U' L' U L F)
U (R' U R' U) R2 U (R2' F R F' R') (U2' R U' R)"
(r U' r' F) (R' F' R U2) M' U' M
U2 (r U' r' F) R' U (F U' F' U') R
U2 (L F' L' U' L F L' F' U F2) (R U R' U' F')
U' (R' U2 R U) R2' (F' U' F U) R2 U2' R' U' R
U'↑r' U2 (F' R U R' U' R' F R) U2' r
U2' (L F' L' U') F' U (L' U' L U) (L F L') (U2' R' F2 R)
"(L f' L' U') (L f L') (f' U f)
 U2 (R U' R' U') F' U (R U R' U') R' F R"
U' L U F U2 (R U' R' U) (R U2' R' U) F' U' L'
(MR U' R' U') (F' U2' F U2) r U2' R'
U2 (R U' R' U') (R U R2' U' F' U F R2 U R')
U2 (R U' R' U') (R U2' R' F') (r' U' F' U F r) F
U (R U' R' U) (R U R' U') (R U' R') (F' U F) (R U R')
U F' (L' U L U') (L' U2 L U) F
r' D (R2 U R' U) (R U' R2') D' r
"U F' (L' U2 L U) (L U2 L' U' L U' L') F
 U' (R U R' F') (R U R' U R U2' R') U' F R U' R'"
U (R' U' R U' R' U2) (R2 U2' R' U2 R' F R F')
R' U F' U F (R U' R' U') (R U' R' U R)
U' (R U R' F') (R' U2' R F) U' (R' U' R U) R U' R'
(F' U2' F U') (R U R' U) (R U R' U') F' U2' F
U2 R' U' F R' F2 (R U R U') R' F R
U (↑B U2 B') (R2' F' L F' L' F2 R2)
U f' (L' U L U') S (L' U2 L U) F
U (↓R U2 R D R' U2 R D' R2') (F U R U' R' F')
U' (R U R' U' R' F R F') U (f U R U' R' f')
U (R' F R' F' R2) U' f R' f'
U l' U2 L U L' U l
U' (r' U2' R2 U R2' U r) (U' R U' R')
U' F (R U' R' F') U' r' F U' F U r
U2 M' U (R' U2' R U R' U R) M
(R U R' U) (R U r U') r' F U R' F U' F'
R' F' U2' (R U R' U R U2 R') F R
U (f U R U' R' f') (R B U B' U' R')
"U2 (L' B' U' B U L) (f' U' L' U L f)
(R' F' U' F U R) U (R' U' F' U F R)"
U' (F R U R' U' F') (R' F' U' F U R)
U2↑R' U' (R' F R F')2 (R U' R' U2 R)
U' (F' U' L' U L) (U' L F' L' F U F)
(R U R' U') F' U' (R' F R U) (R' F' R F)
U2 f R f' R2' D' (r U' r' D) R2
U' (R2' F R F' R) U2 (R' F' U2' F R)
U2 (R' U R U) R' (F R' F' R2 U' R') (F' U' F U') R
U' R' U' (R F R' U) (R U' R' F') (R U R U') R'
U' (L' U R U' L U R') U' (F' U' L' U L F)
U2 F (R U R' F) U (R U' R' F') (R U R' U2) F'
R D (r' U r D') R2' U' F' U' F R
U2 (R U' R' U') F' U2 F R' F (R2 U' R' U') (R U R' F')
U' (R U2' R2' D' R U R' D R) U (R' F R F')
U (R U' L' U R' U' L) (F' U' L F' L' F U F)
U' (R' F' R U2) (R U2 R' F2) (R' F' R U') R U' R'
"U' (M' U L' U' l) (F U2' F') (l' U l)
(r U r') (F' U2 F) (r U' R' U M)
U' F' U' (L' U S L U L' S' L) U' F 
U'↑ R' U' (F R' F' R) U R
(R2' U R2 S R2' S' U' R) (F' U' F U R)
U2 F' (L' U L U2') (L' U' L F)
U2 F' (r U' r' F') R' F' R2 U2' R'
(L' U' L U' L' U2 L) (f' L' U' L U f)
"U' (L U F U' F' L2') (U' L U' L' U2 L)
 (f R U R' U' f') U (R' U' R U' R' U2' R)"
"U' F' (U' L' U L) F
U2 R' U' F' U F R"
U r2' U' (M' F R F') (R U' R' U) r' U r2
U2 (S' R' U' R S) (R' F' U F R)
"U↑r' U' (M'R' F R F') M U r
U2 r D' (R2' U R U) (R' U2' R2 D r')"
U' (R' U2' R U R' U R) U (R' U'·F R' F' R U R)
U2 (L' U2 L U2' L F' L' F) (R U2' R' U' R U' R')
U2 (L' U2 L U) (F U F' U') (L' U2 L)
U2 (R U2' R') (F R' F' R) U2' (R' F R F')
U2 F U R' U2' (R2 U R2' U) R F'
U2 (R' F' r U R U2' r') (F' R' F' R2 U2' R')
U2 (L' U' L U) (L F' L2' U L U2') (L' U' L F)
U' (L' U L) (F U' F') (L' U' L U') (L' U L)
U2 (L' U' L U L F' L' F) (R' U' F' U F R)
(R' U' F U R U' R' F' R) (F' U' L' U L F)
"U (F R' F' R) (U R U R') (F R' F' R2 U2' R')
U2 (R U2' R' U' R U' R') U' (F R' F' R U R U' R')"
U2 (r U R' U' r' F R F') (R' U' F' U F R)
"U2 (l' U' L U) l F' (L2' U L U2) (L' U' L F)
U2 (R' F' r U R U' r2') (F r F R U' R')"
U2 (R U2' R' U' R U' R') (F' L F L' U' L' U L)
U r' U' R2 D (R' U' R D') R2' U2' r
U2 F (R U' R' U') (R U R2' F') (r U R U' r')
U (R' F R U) F2 (R' F' R U') F' M' U2' M
(f' U f U2) F R' F' U2' R2 U2' R
U2 F' (L F' L' F) (L' U L F) (U' R U' R')
(R U' R' U) (R U' R' U') (F R' F' R2 U R')
U2 (F' L F L' U' L' U L) (R' U' F' U F R)
"U2 (F' L F l') U2 (F' L F L') (U L' U l)
 U (R' F R U) (R' U' R' F') R F' U F R"
U r2' D' (r U' r' D) (r2 U' R' U) M U r
U2 (R2' U' R U) (R U R' U') (R' F' U F) R U' R
(MR U' R' U r U' R') U' (F R' F' R2 U R')
U (R' F' U' F U R) U2 (R U2' R' U2 R' F R F')
U (F R' F' R U R U' R') U2 (F' L F L' U' L' U L)
U2 (R U' R' U') F' U2 F (R' U2' R U) (R U' R2' U2') R
U' M' U' (R2 D r' U2 r D' R' U2 r')
U2 (R U' R' U') (F' U2 F U) (R U' R')
U2 (F' L F L' U2' L' U2 L) U' (l' U2 L U L' U l)
(R U' L' U R' U' L) (F' U' L' U L F)
U' (R' U' F' U F R2) (U2' R' U2 R' F R F')
U2 (F R' F' r U R U' r') (R' U' F' U F R)
"U2 (F' L' U L2 F l') (U' L' U l2 F' l')
(R' U R U2) (R' U' R U2) (R' F R' F' R2)"
U2 (R U' R' F') U F (R U R' U) (R U R' U') R U' R'
U2 F' L' U L (R U R' U') (R' F R2 U' R')
U2 (L' U2 L2 F' L' F L' U2 L) (F' U' L' U L F)
U2 (r U R' U R U2' r') (R' U' R U' R' U2 R)
"U' (l' U2 L U L' U l) U (l' U' L U' L' U2 l)
U2 (R' F' U' F) (R' F R F') (R U' R' U2' R)"
U2 (l' U2 L2 F' L' F2 U' F') (U L' U2 l)
U (R' U2' R U R' U R) U (r' U' R U' R' U2 r)
U (L' U' L U' L' U2 L) U F' (U' L' U L)2 F
U2 (l' U' L U' L' U2 l) U' (l' U2 L U L' U l)
U2 (L' U' L U) L F (l' U l F2') L2' U2 L
U (r' U2' R U) (R2' F R F') U (F' U' F U) r
U2 (r U R' U R U2' r') U (R U2' R' U' R U' R')
U2 F (R U R' U')2 F' (R' U2' R U R' U R)
U' R' F' U2' (R U R' U) F2 (r U2 r' F) R
U' F (R U' R' U) R U2' R2' U' F' U F R F'
U' f R2 D (R' U R D') R2' U' f'
U' F (R U2' R' F') U2 F (R' F R F2)
U2 F R F' U (R U R' U') (R' U' R U) (F' U' F U') R'
U F U (R U2' R' U) (R U R2' F') (R U R U' R')
U (R U' L' U R' U' L) U (F U R U' R' F')
U F U2 (R U' R' F) (R U R' U') F' (R U' R' F')
U2 F U (R U R' U2') (R U R' U2') (R U R' U) F'
U2 R' D' (r U' r' D) R2 U' (R' F' U F)
U (L' U2 L2 D L' U' L D' L') U' (L F' L' F)
U F' U' F (R U R' U2') (R U R2' F R F') U F' U F
U' (L' U R U' L U R') (F U R' F R F' U' F')
"U (M' U' R U r') (F' U2 F) (r U' r')
U F U (R U' S' R' U' R S R') U F' 
U'↑ l U (L F' L' F) U' l'
"(L2 U' L2' S' L2 S U L') (F U F' U' L')
U' F (R U2' R' U') (M' U R U' r') U' F'"
U2 F (R U' R' U2) (R U R' F')
(R U R' U R U2' R') (f R U R' U' f')
(R U2' R2' F R F) (r U r' F)
U (R' U' F' U F R2) (U R' U R U2' R')
"U F (U R U' R') F'
U2 L U F U' F' L'"
U2 (R' U' F' U F R) U' (r U R' U' M U R U' R')
U2 (S L U L' S') (L F U' F' L')
"U (L U2 L' U' L U' L') U' (L U· F' L F L' U' L')
 U' (R U2' R' U' R U' R') (F U R' F R F' U' F')"
U'↑ l U (M' L F' L' F) M U' l'
U2 (R U2' R' U2 R' F R F') (L' U2 L U L' U L)
U2 (R U2' R' U') (F' U' F U) (R U2' R')
U2 (L' U2 L) (F' L F L') U2 (L F' L' F)
U2 F U (R U2' R' U) (R U2' R' U') F'
U2 (R U R' U') (R' F R2 U' R' U2) (R U R' F')
U (R U' R') (F' U F) (R U R' U) (R U' R')
U2 (R U R' U' R' F R F') (L U F U' F' L')
(L U F' U' L' U L F L') (F U R U' R' F')
"U2 (L F l' U' L' U2 l) (F L F L2' U2 L)
 (R' U' R U' R' U2' R) (F U R U2 R' U' R U R' F')"
U' (F' L F L') (U' L' U' L) (F' L F L2' U2 L)
U (r U r' U) (R U' r U') (r' F R' F')
U2 (r U R' U') r' F (R2 U' R' U2') (R U R' F')
U (R B U B' U' R2') (F2 r U2' R U' r' F)
U2 F (R U' R' U') R U R2' F' (R U R U') R'
U' M U' (R' F R U) (R' F' r U) F U2' F'
U' (M U R2' D') (r U2 r' D) R U2 r
U2 (L' U L U) (F U2' F' U') (L' U L)
(L' U R U' L U R') (F U R U' R' F')
U2 (F R' F' R U2 R U2' R') U (r U2' R' U' R U' r')
U (L U F U' F' L2') (U2 L U2' L F' L' F)
U2 (F' r U R' U' r' F R) (L U F U' F' L')
"U2 (F R U' R2' F' r) (U R U' r2' F r)
U2 (R U' R' U2') (R U R' U2') (R U R2' F R F')"
F (R U' R' U') (R U2 R' U') (R' F' U' F U R) U' F'
U2 F R U' R' (L' U' L U) (L F' L2' U L)
U' (r U' r' U') F2' (r U r' U) F M' U2 M
U (r U R2' D') (R U R' D) R2 U2' r'
U2 F' (L' U L U) (L' U' L2 F) (l' U' L' U l)
U2 (L' U2 L U L' U L) (F R' F' R U R U' R')
U2 F (R' F R F') (R U' R' F') (U L' U L)
(L' U L U') (L' U L U) (F' L F L2' U' L)
"U2 (F R' F' R U R U' R') (L U F U' F' L')
 U2 (F R' F' R U R U' R') U' (F U R U' R' F')"
"U2 (F R' F' r) U2' (F R' F' R) (U' R U' r')
U' f (R U' R D) (R' U2 R D') R2' U' f'"
(f U' f' U2') F' L F U2 L2' U2 L'
U (r U' r' F') U (R' U' F' U F R) F r U r'
(R2 U R' U') (R' U' R U') F' U' F (R U2 R' U) R'
(ML' U L U' l' U L) U (F' L F L2' U' L)
U2 (R U2' R2' F R F' R U2' R') (F U R U' R' F')
(r' U' R U' R' U2 r) (R U R' U R U2' R')
"U (r U2' R' U' R U' r') U' (r U R' U R U2' r')
U2 (r U R' U') (r' F' r U') (r' F2 R2 U2' R')"
U2 (r U2' R2' F R F2' U F) (U' R U2' r')
U2 (R U R' U R U2' R') U (r U2' R' U' R U' r')
U' (R U R' U R U2' R') U' F (U R U' R')2 F'
U2 (r U R' U R U2' r') U (r U2' R' U' R U' r')
U2 (r' F' r2 U' r') F2 (R U' R' U) (R U' R' F')
U2 (R U R' U') R' F' (r U' r' F2) R2 U2' R'
(r' U' R U' R' U2' r) U' (R' U2' R U R' U R)
U2 F' (L' U' L U)2 F (L U2 L' U' L U' L')
F (R U R' F) (R' F' R2 U' R' U) (R U' R' F')
U' R U' (F' U' F) R' U' (R S R S') U' R'
(R U' R' U') R' U' (F' U F U2') R2 U R2' U R
U' M' U (R U' r' U) (R U R' U) F' U F
U' (R' U2' R U R' U) (r U R U' r' U' F' U F)
U' (R' U R U') (R' U R U) (R' U F' U F U R)
"U' (l' U' L2 F' L' F L' U l) F U' F'
U' (F' L F L' U' L' U L) U' (L U2 L' U' L U' L')"
U (R U R' U) F2 (r U2 R' U') r' F R
U' (↓r U2 R' U') R2 U' (r' F R' F')
U R' U' F' U2 F2 U (R U' R' F') U' F' U' F R
U2 (R' U R2 D) (r' U' r D') R2 U2' F' U F R
U' (R U R' U R U2' R2') (U r U R' U' F' U' F R M)
U' (R' U2' R U R' U R) (F R' F' R U R U' R')
"U' S (R U' R' U') (F' U2 F) (R' F R f')
U (R U2' R2' F R F') (r U' R' U) (R U2' R' U') M
U2 R2' D' (r U r' D) (R2 U' r' U') R U M'
U' (R U2' R' U' R U R' U' R U' R') (F U R U' R' F')
(F R' F' R) U (R' F' U' F U R) U2 (R' F R F')
(R' U2' R U2) F (R U R' U') (R' F' U F) R F'
"U (l' U2 L U L' U M) (U2 L F' L F L2' U2 L)
U' R' U R2 U (R2' F R F') U F R' F' U R"
U' (R' U2 R U) (R' U' R U) (R2' F R F') U R
U (R' U2' R U R' U' R U R' U R) (F R U R' U' F')
U (R' U r U) (R' U' R2 D) (r' U' r D') r'
"U' L U2 (L' U' L U) (L' U' L) (F'· L F L') U' L'
 U (R U2' R' U') (R U R' U') (F' U2 F) (U R U2' R')"
(r' F R F') (r U' R2' U') (F' U F) (R2 U' R')
U (F R' F' R) U2' (R' F R F') (R U2' R')
U' (R U R' U) (R U' R2' F') U' F U (R U' R U') R'
"U' F (R U' R' U2) (R U R2' F') (r U R U' r')
U (L' U2 L2 F' L' F') (R' F2 R U R U' R')"
(R U2' R' U') (F' U F U) (R U2' R')
R' U' R' F (R2 U' R' U2') (R U R' F') R
U' (R' F' U' F U R) (F' L F L' U' L' U L)
U R' U' (F' U' F U) (R U2 R' U' R)
U R' F' U2 (R U R' U) (R U' R' U') (R' F R U) R
U' R2 D (R' U R D') R' U R' U2 (R' F R F')
U2 (L' U2 L U L' U L) (R U R' U' R' F R F')
U2 R' D' (r U' r' F2) (r U' r' F') D R
"U' (L' U' L U2) (L F U F') (U' L2' U' L)
 U (R' U' R U) (f U R U' R' f') (U R' U' R)"
U' S U F U' f' (U2' L' U2 L)
U2 (R' U' R U) (R' U R U) (R U R' U') (R' U' F R F')
"U' (↓ F' U' L' U F) (l' U' L U l)
U2 R' U' F' U (R U R' U') (R' F R U) R"
U (R' U2' R U) F U' (R' U2' R U2) (R U' R' F')
U2 (F R' F' R) U (R U R' U') R U' R'
U f' (L' U L U') S (L' U' L F)
U (R' U' R' F R F' U R2) (U R' U' R' F R F')
U2 R' D' (r U' r' D) R F' U F
U' F' U2 F2 U (R U' R' F2) U F
U'↑R2' F2 (r U r' F') (r U' R U2') r' F R
U' F' (L' U' L U)2 F (l' U' L U l F' L' F)
U' F U R' U2' (R2 U R2' U) (R2 U R' U') F'
U' R' U' (F U R U' R' F') R
"U' F' U (L' U' L2 D) (L' U L D') L' U2' F
U' F R2 U2' (R' U2 R' U') F R F' R' U F'"
U' (R' F R U') (R' U2' R U) R' F' U R
(F' L F L' U2' L' U2 L) (f' L' U' L U f)
U R' F (R U R' U') (F2 U F R)
(R U' R' F) U (R U2 R' U) (R U2 R' U') F' R U2 R'
U S' (L' U' L U L F' L' f)
(F' L F L' U' L' U L) (R U R' F' L' U' L F)
U' F' (L' U' L U)2 (L' F l' U' L U l)
U2 R U R2' (F' U' F U) (R2 U' R' U) R U2' R'
M U r' U' (R' F R U) (r U' R' F') r
U2 F (R U R' U')2 F' (R U' L' U R' U' L)
(F' L' U' L U F) (L' U2 L F' L F L2' U2 L)
U' R' U' (R U2 R' U2') F' (r U' r' F2) U R
(L U L' U L U2 L') F' (U' L' U L)2 F
(r U2' R' U' R U' r') U (r U R' U R U2' r')
(R U2' R' U' R U' R') U (r U r' U R U' M' U' r')
U' (F' L F L') U2' (L2' D' l U2' l' D L2)
(L' U2 L2 F2') (l' U' l F') (L' U' L' U L)
U2 F (R U R' U')2 F' (R U R' U R U2' R')
(R U2' R' U' R U' R') U (r U R' U R U2' r')
U' (L U2 L' U' L U' L') U' F' (U' L' U L)2 F
U2 (R U R' U R U2' R') F (U R U' R')2 F'
U2 R' U' (F R' F' R) U' (R U R2' F R F') U R
U L' U (F U F') L U (L' S' L' S) U L
U R' U' R2 U' R2' U2' (F' U' F U) (R U R U R')
U M' U' (L' U l U') (L' U' L U') F U' F'
U' (R U2' R' F) (R' F' U' F') U F R2 U' R'
U (L U' L' U) (L U' L' U') (L U' F U' F' U' L')
"U (r U R2' F R F' R U' r') F' U F
U (F R' F' R U R U' R') U (R' U2' R U R' U R)"
U2 F' (r U' r' F2) U2 (R' F R U) (R U' R' F')
U (↓ l' U2' L U) L2' U (l F' L F)
U2 F U (R U2' R2' U') (F' U F) R U (R U R' F')
U (R2 D R' U2' R D' R' U2 R') (F U R U' R' F')
(R' U2' R2 U2' R2' U2') (R' F R F') (R U R U') R2' U R
U (L U2 L' U' L U' L') (F' L F L' U' L' U L)
"U S' (L' U L U) (F U2' F') (L F' L' f)
 U' (R2' U' R U) (R U' R' U') (F R' F' U R2)"
"U' (L' U2 L2 F' L' F) (l' U L U') (L' U2 L U) M
 U F U (R U' R' U') F' U2 F (R' U2' R U R' U R) F'"
R2 D (r' U' r D') R2' U (r U R' U') M
U (L' U2 L U L' U' L U L' U L) (F' U' L' U L F)
U (R U2' R' U' R U R' U' R U' R') (F R U R' U' F')
U2 (R U2' R' F') (r' F' r2 U2') (R' U' R U') r' F
U' (r U2' R' U' R U' M) (U2' R' F R' F' R2 U2' R')
U' (R U2' R' U') R U R' (F R' F' R2 U2' R')
U' (L U2 L' U' L U L' U' L U' L') (F' L' U' L U F)
"U R' U2' (R U R' U') (R U R') (F·R' F' R) U R
U' r' U' (R' F R F') (R U' R' U) (R U' R' U2) r"
U (R U' r' U') (R U R2' D') (r U r' D) r
(l F' L' F) (l' U L2 U) (F U' F') (L2' U L)
"U' (F' L F L') U2 (L F' L' F) (L' U2 L)
U x' (R U R' D) (R U' R U') (R' U R' D') x"
U' (R' U' R U') (R' U R U) (F R U R' U' F') R' U R
"U F' (L' U L U2') (L' U' L2 F) (l' U' L' U l)
U' (R U2' R2' F R F) (L F2' L' U' L' U L)"
(L' U2 L U) (F U' F' U') (L' U2 L)
(R U2' R2' U') F' U (R U R U') (R' F R U') R'
U (L F U F' U' L') (F R' F' R U R U' R')
U' L U (F U F' U') (L' U2' L U L')
U2 F U (R U2 R D) (r' U2 r D') (R' U' R' F')
U' R2' D' (R U' R' D) (R U' R U') (R' F' U F) U' R
U2 (R U2' R' U' R U' R') (L' U' L U L F' L' F)
"U2 L D (l' U l F2') (l' U l F) D' L'
(R U R' U') (R' U2' R U R' U R) U2 (R' F R F')"
U (R U R' U2') (R' F' U' F) (U R2 U R')
(F R' F' R U2 R U2' R') (f R U R' U' f')
U L U (F' U' L' U L F) L'
U F U' (R U R2' D') (R U' R' D) R U2 F'
U' (r U r' U) F U2 (r U' r' U') F' U' F'
U (r U' r' F) U F (R U' R' F')
U' S (R U R' U') (R' F R f')
U' L F' (L' U' L U) (F2' U' F' L')
(F R' F' R U R U' R') (L' U' L F R U R' F')
U↓F (R U R' U')2 (R F' r U R' U' r')
U2 (R' U2' R U2) (R' U R U2) (R' F' U2' F R)
U2 (R' U2' R U) R' U' F' U' (R' F' U' F U R) F U2' R
U F' U (R U R' U') (R' U' F2 U) (R2 U' R' F')
U S' U' F' U f (U2 R U2' R')
R U R2' (F' U' F U) R U' F' U2 F R U' R'
U (↓F U R U' F') (r U R' U' r')
x' U' R U R' x U' (R' U' R U) R' U R
U R' U' (F' U F U2) R' D' (R U2 R' D) R2
U' f (R U' R' U) S' (R U R' F')
U2 F (R U R' F') U F U (R' F R F') (R U R' F')
R D (r' U r D') (R' f R' f')
U↑ L2 F2' (l' U' l F) (l' U L' U2) l F' L'
(R U2' R2' U') (F' U F) R2 U' R'
U F (R U R' U')2 F' (r U R' U' r' F R F')
U2 (F' L F L' U' L' U L) U' (R U R' U R U2' R')
(F R U R' U' F') (R U2' R' F R' F' R2 U2' R')
U' (R U R' U2') F2 (r U r' F) (U2' R U' R')
(R' U' R U' R' U2' R) F (U R U' R')2 F'
"(l' U2 L U L' U l) U' (l' U' L U' L' U2 l)
U2 (R' U2' R U R') (F R' F' R) (F' U F R)"
"(L' U2 L U L' U L) U' (l' U' l U' L' U M' U l)
U2 (R' F R U) R U2' R2' F (r U' R U') r2' F r"
U (F R' F' R) U2 (R2 D r' U2 r D' R2')
(R U2' R2' F2) (r U r' F) (R U R U' R')
"U2 F' (L' U' L U)2 F (L' U' L U' L' U2 L)
U2 (r U R' U R U2' r') (R' F R2 B' R2' F' R2 B R')"
U2 (R' U2' R U R' U R) U (l' U' L U' L' U2 l)
U (R' U2' R U R' U R) U F (U R U' R')2 F'
U R' U' (F' U F U2) L (R U' R' U) L' U2 R
(R U2' R' U) F' U' F2 (R' F' R2 U2' R')
U (↑R' U R U') (R2' F R2 U R' U') F' R
U'↑ l U' (L F' L2' U' L2 F L') U F l'
U' (R U R2' F R F') U (F R' F' R)
"U2 (R U R' U R U2' R') (L U F' U' L' U L F L')
U' (R U R' U) (F' U F U') (R U' R' U') (R' F R F')"
U' F U2 (R U R' F) R' F' R2 U2' R' U F'
"(R' U' R U' R' U2' xM) (U' L U L F' L' F)
 U' (R' U2' R U) R' U F2 (r U2 R U') r' F"
U (R' F R F') (r U' R' U') (R U' R' U2) M
U (R' F R F') U2 (r U' R' U M) (U2 r U r')
U' (r' U' R U') R2' D' (R U R' D) (R2 U' R' U2) r
U2 (R U R' U' R' F R F') U (r' U2' R U R' U r)
U2 (r U R' U) (R U r' F) U F (R U' R' F')
f' (L' U L U2') L F L' (U2' L' U2 L) F' U f
U (R' U' F' U F R) U' (R U R' U R U2' R')
U2 R U2' R' (L' U2 L U L' U L) U (F' L' U' L F)
(R' U2' R U R' U R) (f R U R' U' f')
U R2' U (R U' R' F) R' U R2 U' F' R'
U' (↑ L U L' U L U2' L') U (L U L F' L' F U' L')
U2 (R' U2' R2 U R2' U) (F R F' R U2' R')
(r' U2' R U R' U r) U (L' U' L F R U R' F')
U (R B U B' U') (R2' F2 r U r' F R)
U' (L' U' L U' L' U L) (F R U R' F')
(L' U2 L2 F' L' F) (L U L2' U L2 U2 L')
U2 (R U2' R' U' R U' R') (F R U R' U' F')
U2 (l' U2' L U L' U l) (F U R U' R' F')
U' (l' U' L U l F' L' F) U' (F' L F L' U' L' U L)
U2 (R' U' F U R U' R' F' R) U' (R' U2' R U R' U R)
U' (L' U' L U L F' L' F) U' (F' L F L' U' L' U L)
R B' R' F R B2 U' B' U R' F'
U2 F (R U' R' U') (R U R' U) (R U' R' F')
"U2 (R' U' F U R U' R' F' R2) (U R' U R U2' R')
U' F' U' F (L' U2 L U2') (L F' L2' U' L F)"
(R' F R U R' U' F' U R) (F U R U' R' F')
(L F' L' U' L U F U' L') (f' U' L' U L f)
"U' F' U' (L' U L2 F L' U' L' U' L) (F' L F L2' U2 L)
U2 (r' U r' U) (r2 U r2' U') r F' U' F r"
U2 (r U R' U) (R U' R' U') (r' F' R U2) (R U2' R' F)
U (r U R U') r' F (R' U R U') R' F'
U (F R' F' r U R U' r') (F U R U' R' F')
"U (F' L' U L U2 L' U' L F) U (R U' L' U R' U' L)
U F U (R' F R F') (R U2 R' U) (R U R' U) (R U' R' F')"
U2 (R U' L' U R' U' L) (F U R U' R' F')
U'↑R' U' F' U (L' U2 L U) (L' U' L U') F R
L U (L' U L U') (F U F' U') (L' U2' L U L')
U2 (R U R' U') (R' U R U2) R' U' (F' U F U) R2 U2' R'
(f' L' U' L U f) (R U' L' U R' U' L)
U2 (R U2' R' U2 R' F R) (U R' U' R F' R' U R)
x'· (R U' R' D) (R2 U R' U R' D') (R U' R') x
R' U' (F U R U' R' F) R2 U2' (R' F' R U2') R2' F2 R
U2 (R U R' U) (R U' R' U2) (R' F' U' F U R2) U R'
U2 (R U2' R' U2 R' F R2) (U' R' U' R U2' R' U' F')
"U' L F2' (l' U' l U') F' L2' D' (l U l' D) L
U (R U R' U R U' R' U R U2 R') U' (R U R' U' R' F R F')"
U (R U R2' U') (R' F R F') U F (R U R U') R' F'
U (L U' L' U2') L U (F U' F' U) (L' U' L U') L'
R' F (R U R' D) (R2 U' R2' D') F' R
U' (R' U2' R U R' U R) U2 (F U R U2' R' U' R U R' F')
(L' U R U' L U R') U (r U2' R' U' R U' r')
U2 (R' U' R F R' U R U') (R' F' R U2 R U2' R')
U2 (L' U R U' L U R') (f R U R' U' f')
U' (R U R' U) F' (R U2' R' U2) R' U' F U R
U (r' U' R U2) (R' U' r U) (r' F' U' F) (r U r' U) r
U2 (R' F R U) (R' F' R F) U' (R U' R' U2') (R U R' F')
(F R' F' R) U2 (r U' R' U) (R U2' R' U') M
U2 (L' U R U' L U R') U' (F R U' R' U2 R U R' F')
U' (↑ L U L F' L' F U' L') (· f' U' L' U L f)
"U (l' U2 L U L' U l) U (L' U2 L U L' U L)
 (r' U2' R U R' U r) U (R' U2' R U R' U R)"
U R' F R2 B' R2' F' R2 B R'
U (↑R' U' R' F R F' U R) (F U R U' R' F')
(R u R' U) (R' U' R u') R2' U2' R
U2 F (R U' R' U) (R U2' R2' U') R F' R' U R
U (L' U' L U' L' U2 L2) (F2' l' U' l F' L')
U2 (R' U2' R U) R' U F' U' F (R' F R F') U R
U' (F' U' L' U L F) (f R U R' U' f')
U' (F R U R' U' F') (L U L F' L' F U' L')
(r' F' U' F) U F' r F (R U R' F')
U' (F R U R' U' F') U2 (R' U'·R' F R F' U R)
U' (↑ L U' L' U) (L2 F' L2' U' L U) F L'
U↑r' U (R' F R2 U R2' F' R) U' F' r
U (L' U' L2 F' L' F) U' (F' L F L')
U2 (L' U' L U' L' U2 L) (R' U' F U R U' R' F' R)
(L U L' U L U2 xM) (U R' U' R' F R F')
U' (r U' r' F) (R' F r U) (L' U L U2) M
U2 (F R' F' R) U (R' F R F') (R U' R' F') U F
"U' (L F' L' F) U2' (l' U L U' M) (U2' l' U' l)
U' (R' F2 R F') (r U' r' F) (r U r' F) r' F2 r"
U' (r U R' U) R2 D (R' U' R D') R2' U R U2 r'
"(R' U' R U' R' U2') (F R U R' U' F2 U F R)
U2 (L' U' L U L F' L' F) U' (l U2 L' U' L U' l')"
U (R U R' U) (R U' R2' F R F' R) U R' U' F' U2 F
f (R U' R' U2) R' F' R (U2 R U2' R') F U' f'
(R' U2' R U R' U R) (F R U R' U' F')
U2 L' U2 L (R U2' R' U' R U' R') U' (F R U R' F')
(L U2 L' U' L U' L') (f' L' U' L U f)
U (↑R' U' R U' R' U2 R) U' (R' U' R' F R F' U R)
U2 (R U2' R' U') (R U' R2' U') (·F R' F' R) U R
"U2 (L U2 L2' U' L2 U') (F' L' F L' U2 L)
U (r U r' U) (R U' R' U) (R' F R F') (U' r U' r')"
(l U2' L' U' L U' l') U' (R U R' F' L' U' L F)
U (r U R' U R U2' r2') (F' U' F U r)
U (R U R' U R U' R') (F' L' U' L F)
U2 (L' U2 L U L' U L) (F' L' U' L U F)
U2 (r U2' R' U' R U' r') (F' U' L' U L F)
(R U2' R2' F R F') (R' U' R2 U' R2' U2' R)
U (r U R' U' r' F R F') U (F R' F' R U R U' R')
U (R U R' U' R' F R F') U (F R' F' R U R U' R')
U' (R' F2 r U r' F R) U (R' U' F U R U' R' F' R)
U' F' (r U R' U') r2 F r U' F R
U2 F' (L' U L U) (L' U' L U') (L' U L F)
"U2 (L U F' U' L' U L F L2') (U' L U' L' U2 L)
U' F U F' (R U2' R' U2) (R' F R2 U R' F')"
U (R' U R U2') (R' U' R U') (R' F' U' F) U' R
U F U (R U' R2' F' R U R U R') (F R' F' R2 U2' R')
(R' F R U R' U' F' U R) (f U R U' R' f')
U2 F U2 R2 U2' R' U2 (R' F R F') R' U2 F'
U' (F' r U R' U' r' F R) (F' U' L' U L F)
R' U' R F U' (R' U2' R U2) (R U' R' F')
U' (F R U' R' U2' R U R' F') U' (L' U R U' L U R')
U↑ L U F U' (R U2' R' U') (R U R' U) F' L'
U2 (L' U R U' L U R') (F' U' L' U L F)
"R' U' (R U' R' U) (F' U' F U) (R U2 R' U' R)
(R U R' U) R d' (R U2' R' U') (R U R' F')"
U' (R' U2' R U) (R' U' R U) F (R2 U' R' U) R U R F'
(f R U R' U' f') (L' U R U' L U R')
"U2 (L' U2 L U2' L F' L') (U' L U L' F L U' L')
U (F U R U2 R' U' R U R' F') U2 (R' U' F' U F R)"
U' (R U2 R' U) (R U R' F) R' F' R2 U2' (R' U R U') R'
"U2 x· (R' U R D') (R2' U' R U' R D) (R' U R) x'
(R U R' U) (R U' R' U) (R' U' F' U F R2) U' R'"
U2 F R F' U' (R' F' U F) R2 U2' R' U2 R'
U2 (R' F R U) (R' F' R F2) (R' F' R U') F'
U R' F2 (r U r' U) F R2 D (r' U' r D') R'
U2 F' (R U2 R' F2) (r U2 r' U) (L' U L F)
U' (R' U R U2) R' U' (F' U F U') (R U R' U) R
L F' (L' U' L D') (L2' U L2 D) F L'
U' (F R U' R' U R U2' R' U' F') U2 (R' U' R U' R' U2' R)
U2 (r U R2' F R F') (R U' r' U') F' U2' F
"U2 (L U L' F' L U' L' U) (L F L' U2' L' U2 L)
U (R' F' U' F U R) U2 (F R U' R' U R U2 R' U' F')"
U2 (R U' L' U R' U' L) (f' L' U' L U f)
(R U2' R' U') F' U (R U2' R' U2) (R' F R2 U' R')
U' F (r U' r' U) (R U2 R' U) (r U2' r' U' r U' r') F'
U (R' F R U2) F U' (R U2' R' U2) F' U' R' F2 R
U' F (R U' R' F') (r U r' U') (r' F r F') U' r' F2 r
U' r U (M U R' U') (r U R' U2) (r' F R F')
U (↑R' U' R' F R F' U R) (·f U R U' R' f')
U' (r U2' R' U' R U' r') U' (R U2' R' U' R U' R')
U R B' R2' F R2 B R2' F' R
U' (F R U R' U') (R U' R' F' U' L' U2 L)
U2 (R' u' R U') (R U R' u) R2 U2' R'
U (R' U' R' F R F' U R) U' (R' F' U' F U R)
U' (R U R' U R U2' R2') (F2 r U r' F R)
(R U2 R' F) (R' F' R F) (R' F' R2 U2' R')
U (F U R U' R' F') (f' L' U' L U f)
U (F' L' U' L U F) (R' U' R' F R F' U R)
U F U (R U' R' U) F' r' U' F' U r
U (F' L' U' L U F) U2' (L U· L F' L' F U' L')
U' (R U R' U') R' F (R2 U' R' U') (R U2 R' U') F'
U' (R U R' U') (R' F R U) R' U' R F' R' U R
U2 (R' U R U') x' U (L' U L U2) (r U' R' U) M x
(F U' F' U2) (L' U2 L U2') (L' U L U) F U' F'
(F' U F U2') (R U2' R' U2) (R U' R' U') F' U F
U (F U F R' F' R U' F') (R U' L' U R' U' L)
U' (F' U' F' L F L' U F) (L' U R U' L U R')
"U (R U' L' U R' U' L) (R' F' U' F U R)
U↓ F' L2' D' (L U' L' D) L2 U F"
"U' (L' U R U' L U R') (L F U F' U' L')
U'↓F R2 D (R' U R D') R2' U' F'"
(R U2 R' U) F' U2 F' (r U r' F) R U' R'
U F U (R' U' R U) (R U' R' F') U' R' U R
U' F R F' U' (R U' R U) R F' U' F R U' R
"(L F U F' U' L) (U' L2' S' L2 S U L2')
(F U R U' R' F') (r' U2' R U R' U r)"
"(R' F' U' F U R') (U R2 S R2' S' U' R2)
(F' U' L' U L F) (l U2 L' U' L U' l')"
"U' F (R U R' U') F'
U f (U R U' R') f'
L F U F' U' L'"
"U F' (L' U' L U) F
R' F' U' F U R
U' f' (U' L' U L) f"
"(L F U F' U' L') U (R2 U' S' U2' S U' R2)
U2 (↑R' U' R' F R F' U R) U' (R' U' R U' R' U2 R)"
"(R' F' U' F U R) U' (L2' U S U2 S' U L2')
U2 (↑L U L F' L' F U' L') U (L U L' U L U2' L')"
"(R' F' U' F U R') (U' S' U2' S U' R2)
U2 (M U M' U2' M U) (R' U' F' U F r)"
"(L F U F' U' L) (U S U2 S' U L2')
U2 (M U' M' U2 M U') (L U F U' F' l')"
U2 (S' R' U R S) (R' U2' F' U F R)
"U2 (S L U' L' S') (L U2 F U' F' L')
(S' R U' R' S) (R U2' B U' B' R')"
"(R' F' U' F U R) (L2' U S U2 S' U L2')
(R U R' U2) F' U' r' U' F2 U r F"
(R' F' U' F U R) U' (R2 U' S' U2' S U' R2)
U (R U2 R' F') (L' U L U) F U2 R U' R'
U' (R U' R2' F R F') U' F U R' U' F' U R2 U R'
U' F U (R U' R2' F') U2 (R U R' U) R2 U2' R'
"U2 (L' U L2 U) (F U' F') (L' U2' L' U L)
 U' (R U R D R' U' R D' R2') (F R U R' U' F')"
U2 (R U' R2' U') (F' U F) (R U2 R U' R')
U' F (R U R D) (r' U2 r D') (R' U2 R' U') F'
U (R' U' R' F') (R U R U) (R' U' R U') R' U2' F R
R U R2' F (R2 U R' U')↓F2 U2' F
L' U' L2 F' (L2' U' L U)↓ F2' U2 F'
U' (r' U R' F) R F U (F R' F R2 U R' U') r
U (r' U' r F') r' U F' r U F
U' (R B R' F) (R B' U R' U' F')
"U↑R' F' (L' U2 L U')2 F U R
(R' F R F') (L F' L') (F' U F U') (L F2' L')"
U' F U R' U' R F' R' U (F' U' F U) R
U (F' L F L') (f U R U' R' f') L' U L
U' (R U2 R' U) r' U' F' U F2 R F' M'
U' L F' U· (L F' L' U) (L' U' L U') F (L' U' L F) L'
U' R' F' (r U' r' F') (R U R' U') F' U R
U (R' F R U R' U' F' U R) U' (R' U' R U' R' U2' R)
(L' U R U' L U R') (f U R U' R' f')
(F' L F L' U' L' U L) (l U2 L' U' L U' l')
U2 (L' U L F' L F) U (L2' U L2 U2 L2' U' L)
U' F R2 D (R' U' R D') (R' U2 R' U') F'
U' (l' U' L U l F' L') (U' L' U L)2 F
"U'↑ L F (R U2' R' U)2 F' U' L'
(L F' L' F) (R' F R) (F U' F' U) (R' F2 R)
U' (R U R' F') U (R' U2' R U R' U R) U2 F R U' R'"
U' F (R U' R D) (R' U2' R D') R2' U' F'
U' (F R' F' R) (f' U' L' U L f) R U' R'
U' (R' U2' R U2) F (R U R' U') (R' U R U') F'
U R' F U'· (R' F R U') (R U R' U) F' (R U R' F') R
"U L F (l' U l F) (L' U' L U) F U' L'
U' (R U' R' U') (F U R U' R' F) (r U r' F)"
(F R' F' R U R U' R') (r' U2' R U R' U r)
U' (L F' L' U' L U F U' L') U (L U L' U L U2 L')
(R U' L' U R' U' L) (f' U' L' U L f)
U2 (R U' R' F R' F') U' (R2 U' R2' U2' R2 U R')
U2 (F R' F' r U R U') (r2' U' F' U F r)
U (r U R' U' r' F R) (U R U' R')2 F'
"U2 (R U R' U) (R' F R F')2 (R U' R' U R U2' R')
U (F R' F' R) U' F' (r' U2' R U R') F U r F"
U (r U M U R' U' r U' r') U' (R U R' U R U2' R')
U' (l' U' M U' L U l' U l) U (L' U' L U' L' U2 L)
U2↑ L U (F' L F L')2 (U L' U' L) U' L'
U2↑R' U' (F R' F' R)2 (U' R U R') U R
U2 (R U2' R2' F R) (F2 U F U') R U2 R'
R' U' (F R' F' R2 U' R') U (R' F R F') U R
(R U2' R') (F R' F' R) (F' U F) (U' R U2' R')
U' F2' (R U' R' U) (R U R2' F' R F')
U F2 (L' U L U') (L' U' L2 F L' F)
f (U R U' R')2 f' (l' U2 L U L' U l)
U2 (r U r' U2') (R U R' U2') (R U R' U') r U' r'
"U' (R' F R U) (R' F' R U2') (R F R' U) R F' R'
U (R U R' U' R' F R F') U (R U R' F' R U R' U' R' F R2 U' R')
 U (r U' r' U') (r U r' U2) r' D' (r U' r' D) r"
U'↑ l U' (F' L F l') U (L' U' L U' L' U') (l U l')
U↑r' U (F R' F' r) U' (R U R' U R U) (r' U' r)
(f R f' U) (R' U R U) (r' U' R U M')
(f' L' f U') (L U' L' U') (l U L' U' M')
U (R U R2') (F' U' F U) (F R F') (R U2' R')
U2 F U (R U2 R' U) (R U2' R2' F R F') U' F'
U' (R U2' R2' F) (R2 U R' U') F' (U R U R')
U (L' U2 L2 F') (L2' U' L U) F (U' L' U' L)
"U' (↓R U2 R' U') R2 U' R' F U R2 U' F' U' R' U2 R
U' (R U R' U' R' F R S) (R f' R2' u' R U' R' U R' u R2)"
U' (R' U R U') (R' U' R U2) R' (F R' F' R2 U' R') U' R
U' (R U' R' U) (R U R' U2) (R U R2' F R F') R U R'
(F' U F U) (R U2' R') (F R' F' R)
(F U' F' U') (L' U2 L) (F' L F L')
U2 (R U R' U R U' R' U R U2' R') U2 (R' U' F' U F R)
"U' (f R' F' R) (F' U2 F) (U R U R') S'
"U (f' L F L') (F U2' F') (U' L' U' L) S
 U2 (↑R2' U' F R F') U (R U R' U') (R' U R2)"
"U (F R U R' U' F') (R U R' U R U' R' U R U2' R')
U2 (r2' F2 R U') (R' F R F') (U R' F2 r2)"
U' (F' L' U' L U F) (L' U' L U' L' U L U' L' U2 L)
U2 (R' F' U' F U) (R2 U2' R' U' R U R' U' R U' R')
(R B U B' U') (R2' U2' R U R' U' R U R' U R)
U2 (R U' R2' F R F) r U2' (M U R' U') (r U' r' F)
(R f R f') U (R' U' R U) (R' U' R U') R'
U2 (R' F' U' F) U' (R U R' U') (R U R' U R)
U' (R' U' R U) (R' U' R U) R' F' U2 F U' R
U' (R U R' F') U' (R U R' U') (R' F R2 U' R')
U' (R U R' U R U2' R') (F' L F L' U2' L' U2 L)
"U (L' U' L U' L' U2 L) (F R' F' R U2 R U2' R')
U' F (R U' R' U') (R' F' r U) (R U' r2' F r)"
U' F (R U' R' U2') (R U R2' F' R) (U R U' R')
U F' (L' U L U2) (L' U' L2 F L') (U' L' U L)
U2 (f R U R' U') (S' R U' R' U' R U R' F')
U2 (f' L' U' L U) (S L' U L U L' U' L F)
(R U R' U2') (R U' R' F) (R U R' U') F (r U r' F)
U' (R U R' U') R (F U R U' R' F') U' (R' U' R U) R'
U' F (R U' R' U2) R U R2' F' U2 (R U R U') R2 U2' R
U' (R U R' U2) F' U F (R U' R' U2') R U2 R'
U' (R U R' U') (R' F R F')
U2 (f R U R' U' S') (R' F' R U R U' R')
F (U' R U' R') (F' U' F) (R U2' R' F')
U F' (L' U B' U' B U L U) (L' U2 L U) F
U' F' U' F r U (M U R' U) (r U R' U) M
"U F' U' (L' U2 L2 F L') (U2' L' U2 L) (F' U F)
(R' U2 R' D') (R U R' D) (R2 U' R' U) F' U F R"
F U (l U L' U L U2 l') (F' L' U' L)
"R' U F (U2' r U' r' U2') F' U R
(F R' F' R U R U' R') (L' U' B' U B L)"
"U' (M2' U M2' U2 M2' U M2') (R U R' U' R' F R F')
U (F r U' r' U R U R' U r U' r') (U R U' R' F')
U (L' U2 L U') F (l U2 L' U' L) F' U' l' F'"
"U' F U (R U' R' U)2 (R U2' R' U) (R U R' F')
U' (↑R' U' R U') (R2' F R F' R) U2' (R' U2 F R' F' R2)"
U S (L U F' U' L' U L F L') S'
"U' (R U R' U' R' F R F') (M2' U M2' U2 M2' U M2')
U (F' U2 F U') (R U R' U) (r U' r' U r U r')"
U (L' U' L U) (L F' L' F)
U2 (f' L' U' L U S) (L F L' U' L' U L)
U' R' U F' U F (R U R' F') U2 F R
U' F (R U' B U B' U' R' U') (R U2' R' U') F'
(R2' U' R2 F R' F') U' (R' U R' U R2)
U' F U (R U2' R2' F' R) (U2 R U2' R') (F U' F')
F' U' (r' U' R U' R' U2' r) (F R U R')
"L U' F' (U2 l' U l U2) F U' L'
(F' L F L' U' L' U L) (R U B U' B' R')"
"U (M2' U M2' U2 M2' U M2') (L' U' L U L F' L' F)
U' (F' l' U l U' L' U' L U' l' U l) (U' L' U L F)
U' (R U2' R' U) F' (r' U2' R U R') F U r F"
U F' U' (L' U L U')2 (L' U2 L U') (L' U' L F)
U' S' (R' U' F U R U' R' F' R) S
"U (L' U' L U L F' L' F) (M2' U M2' U2 M2' U M2')
U' F U (R' F R F') U F' U' (R' F R U' R' F' R)"
U2 (R' U2' R U R' U R) (r U2' R' U' R U' r')
(R U2' R' U' R U' R') (r' U2' R U R' U r)
"U2 (R U2' R' U') (R U R') (F R' F' R)2 (U' R U' R')
(F U R U' R' F') (L' U2 L F' L F L2' U2 L)
(F' U' L' U L F) (R U2' R' F R' F' R2 U2' R')
(r U2' R' U) (F' U' F2 R' F' R2 U2' r')
(l' U2 L U') (F U F2' L F L2' U2 l)
(R' F2 R2 U2') (F U F' U) (R2' F2 R)
(L F2' L2' U2) (F' U' F U') (L2 F2' L')
(L' U L U' L' U L) (F' L F L')2
(R U' R' U R U' R') (F R' F' R)2
U2 (R U2' R' U) (F' U' F) (R' F R F') (R U2' R')
(L' U' L U2') (F U' F') (L' U L2 F' L' F)
"(l' U' L U' L' U2 l) (F' U' F L F' L' U L F L')
 U (R U R' U' R' F R2 U R' U' F') (R U2' R' U' R U' R')"
(r U R' U R U2' R') (U R U' r' F R' F' R)
U2 (R' U' R U) (R' U' R U2) (R' U' F' U') F U' R
U (R' F R F') U M U (R U' R' U') r U R'
U2 (R U2' R' U2) (F' U2' F U) (R U' R' U' R U' R')
U (L F' L F L2') U (l U' F U F' l')
(F' U' L' U2 L U L' U' L F) (l' U' L U' L' U2 l)
(L' U2 L U2' L F' L' F) (L' U2 L U L' U L)
(R U2' R' U2 R' F R F') (r U2' R' U' R U' r')
"(r U r' U R U' M' U' r') U (R U' L' U R' U' L)
U' (R U R' U') R U F U2 F' U' (R2' F R U') F'"
(L' U' L U' L' U2 L) (F' U' F L F' L' U L F L')
(r' U' R' F R F' U r2) (U R' U R U2' r')
(F' L' U' L U F) (r U R' U R U2' r')
(F U R U' R' F') (R U R' U R U2' R')
U2 (F' L' U' L F' L F L' U) (L' U' L U F)
U' (R U R' U) (R U' R' U) (F' U F U') R U2 R'
"U2 (L' U2 L F' L F) U (L2' U L2 U2 L')
(R' U' R' F R F' U R) (r U R' U R U2' r')"
U2 (R U R' F') U2 F U (R U' R' U) R U2' R'
U2 r U (M U R' U2') F (R U R') F' U' F'
U (R' U' R U' R' U2') (R2 B U B' U' R')
"U (F' U' L' U L F) (L U2 L' U' L U L' U' L U' L')
(R' U' F' U F R) U' (R U2' R' U' R U R' U' R U' R')"
U (F R U' R' F') (L' U' L U L' U L)
U2 (F' U' L' U L F) (l U L' U L U2 l')
(R' F R U) R' U' F' (R' F R F') U R
(f' L' U' L U f) (L' U2 L U2' L F' L' F)
U' (F R U2' R2' U' F' U F R U2') (R U R' U' F')
U' (f' L F L' U' L' U L) (f R U R' U' F')
F' (L' U L U) (L' U2 L U) (L' U' L U) F
(F R' F' R) U2 (R U L' U R' U' L)
"U (F' L F L' U' L' U L2) (U2 L2' U' L2 U' L2' U2 L)
U' R' F U2' (r U' r' U2') F' (R U2 R' U2' R)"
U (R U2 R' U') (R U R' F) (R U R' U') F' U R U R'
U (F' r U R' U2 r' F2 R2) (U2' R' U' R U' R')
"U (L' U2 L U L' U L) (F R' F' R U2 R U2' R')
U R2 D (r' U2 r D') R2' F2 (r U r' F)"
U' F' U2 F U' (R U R' U) (R U R' F') U F
U' F (R U R' U2) (F' U2 F U) (R U' R' U') F'
U F' U' F2 (R U' R' U') (R U R' F') R U' R'
U' x· (R' U' R D') (R' U R' U R2 D) (R' U' R) x'
(F U R U' R' F') (R U' L' U R' U' L)
U' r' U F' U' F (R U R' U) (R U' r R2' U2' R)
U2 R' U' R (F U R U' R' F') U' (R2' F R F') U R
U2 R U2' R2' (F R U R' U' F') U R (F' U' F) (R U2' R')
U2 (F' U' F U') (F U R U' R' F') (R U' R' F') U F
U2 (r U r' U2) (r U' r' U') F U2 (L' U L U) F'
(F' L' U L F) U (R U L' U R' U' L)
(R U2' R' U2) (R' F R2 U' R' U) (R U2' R' U') F'
F' (r U R' U2) (L' U L U') r' F2 R
U' (R' U R U) (R' U R U') R' U (F' U' F U2) R
U' (r' U' R U' R' U2 r) U' (L' U R U' L U R')
U2 M' U' (L' U2 L U) (r' F' R U2) (r U' r' F)
U' x' U' F' (R U' R' U2') (R U' R' F) R U R' x
(F R' F' R U2' R U2 R') U' (R' U2' R U R' U R)
(F R' F' R) U2 (R U' R' U) R U2' R'
L' D' (l U' l' D) L2 F U (l' U l F2') L'
U' M U (F R U R' U' F') (R' F R F' r U R')
(R U R' U') (R U R' F') U' F U' R U2 R'
U (l' U' L U) (l F' L2' U' L U) (L' U' L U) F
U (R' U R U2' R' U' F' U F U R2) (U2' R' U' R U' R')
U R' F2 r U (L' U' L U2) (R U' r' F)
U' F' U' F (R U R' F) (R U R' U') F' U F' U F
"U' (f' U' L' U L f) (F R U R' U' F')
 U' (r' U2' R U R' U r) (R U R' U R U2' R')"
U2 F (R U' R' F') r' F U' F' U F r
(r U R' U R U2' r') U (R U R' U R U2' R')
U2 (r' U2' R U R' U r) U' (R' U2' R U R' U R)
U (R' F' r U' r' F2 R2) (U2' R' U' R U' R')
U R' U' (R' F R F')2 U R
(r U r' U R U' M' U' r') (R' U2' R U R' U R)
U2 (R U2' R' U2) (R U' R' U2) (r U' R' U2) R U r'
U2 (R' U' R U' R' U2' R2) (U2' R' U' S' R U' R' S)
U' (R U2' R' U' R U' R') U' (r U M U R' U' r U' r')
U' f' (U' L' U L)2 f
U' (R' F R U2) F' U2 F' U2 r U r'
(R U R' U2) (F' U F) (R U' R2' F R F')
(r U R' U R U2' r') (F U F' R' F R U' R' F' R)
"(l' U' L U' L' U2 L) (U' L' U l F' L F L')
U (r' U2' R U R' U r) U' (r U R' U' r' F R F')"
U (r' F R F') (r U' R' U') (S' R U' R' S)
U' F (R U R' U') (R2 D R' U R D' R2' U') F'
U2 (L' U2 L U2') (F U2 F' U') (L' U L U L' U L)
(F U R U2' R' U' R U R' F') (r U R' U R U2' r')
U' (R' F R' F' R2) U' (r' U F' U' F r)
(R U2' R' U2 R' F R F') (R U2' R' U' R U' R')
(L' U2 L U2' L F' L' F) (l' U2 L U L' U l)
(R U R' U R U2' R') (F U F' R' F R U' R' F' R)
(l' U' l U' L' U M' U l) U' (L' U R U' L U R')
(F R U R' U' F') (l' U' L U' L' U2 l)
(R U2' R' U' R U R' U' R U' R2') (U' F' U F R)
(F' U' L' U L F) (L' U' L U' L' U2 L)
U2 (F R U R' F R' F' R U') (R U R' U' F')
U (R U2 R' U) (F' U' F U') (R U R' U') R U' R'
U2 (R U2' R' F R' F') U' (R2 U' R2' U2' R)
r' U' (M' U' R U) r' (F R' F' R) U r
U (R U R' U R U2') (R2' F' U' F U R)
U2 (R U2 R' U') (R U R' U') F' U2 F R U' R'
U' (F U R U' R' F') (R' U2' R U R' U' R U R' U R)
U' (F' L' U L F) (R U R' U' R U' R')
U2 (F U R U' R' F') (r' U' R U' R' U2' r)
U' F R' F' U2 (R U R' U) R2 U2' R'
(f R U R' U' f') (R U2' R' U2 R' F R F')
"U (F' L' U2 L2 U F U' F' L' U2) (L' U' L U F)
U (F R U' R' U' R U2 R' U' F') U (R' F' U' F U R)"
U (f R' F' R U R U' R') (f' L' U' L U F)
F (R U' R' U') (R U2' R' U') (R U R' U') F'
(F' L F L') U2' (L' U' R U' L U R')
U (R U R' U) (R' U2 R' U) (R' U' R U2) F R F'
(F R U R' U' F') (R U2' R' U2 R' F R F')
"U' (R U2' R' U' R U' R') (F' L F L' U2' L' U2 L)
U' L2' D' (l U2' l' D) L2 F2' (l' U' l F')"
"U' (F R' F' R U R U' R2') (U2' R2 U R2' U R2 U2' R')
U2 (R' F R U R' U' F' U R) F (R U R' U')2 F'"
(R U2' R' U) (F' U' F U2) (R' F R F')
U (r U' r' U) (R U R' U) (r U' r' U') F' U2 F
U (R U2' R' U2 R' F R F') (r' U' R U' R' U2 r)
U2 M' U (R U2' R' U') (R U r' U2) (R' F R F')
U' F U (R' F R F2) (R' F R U') R' F' R
(F' L F L' U2 L' U2' L) U (L U2 L' U' L U' L')
U' (R U2' R' U') (R U R' U2) (R' F R F')
R D (r' U r D') R2' F' U' (r U' r' F2) R
U R' U' F' U2 F U' R2 D (r' U' r D') R'
(R U2 R' U) F' U F (R U' R' U) R U' R'
U' (r U R' U') (r' F R2 U R' U') (R U R' U') F'
"U' (L U' L' U2 L U F U' F' U' L2') (U2 L U L' U L)
U (R U R' U) (R U' R2' F) (R2 U R' U') F2 U2 F"
U' (r U2' R' U') (R U R' U2) (r' F R F')
U (R' F' U' F) U (F R U R' U' F') (R U' R' U2' R)
U2 (R U R' F) (R' F' R U) (R U' R' U) F' U F
U' x'· (R U R' D) (R U' R U' R2' D') (R U R') x
(F' U' L' U L F) (L' U R U' L U R')
U' R' U2' R2 r' U (R' U' R U') (R' F' U F) U' r
U (F U R U2 R' U' R U R' F') U' (F R U R' U' F')
U L (R' F' R U2) R' F R2 U2' (R' F' r U2) r2 x
U2 (R' F' R U2) (R' F R U) F' U2 (R U' R' U') F
(F R U' R' F') U' (L' U' R U' L U R')
U (R U R' U) (R' U' F' U F R) F' U F R U' R'
U2 F U (R U' R' U2') (R U' R' F) (R U R' U') F' U' F'
(F R' F' r) U2 (R U' R' U) R U2' r'
(R U R' U) (R U' R2' F') U' F R2 U' R2 U2' R
U (f U R U' R' f') (F' L' U' L U F)
U' (r' U' F U r F U') (R U R' U' F')
U' (r U R' U R U2' r') U' (R U R' U R U2' R')
(r U2' R' U' R U' r') U (R U2' R' U' R U' R')
U' (L F l' U l F2' L2') (U2 L U L' U L)
U l F (R U' R' U)2 F' l'
U2 (R' U' R U' R' U2' R) (r U M U R' U' r U' r')
U2 (R U2' R2' F R F') (R' F R F') R U2' R'
(R U R' U R U2' R2') (U2' R U S' R' U R S)
U2 M U (R U R' U R U2' R2') F2 r U L' U L
U f (U R U' R')2 f'
U (r U' r' U2) (F U2 F U2) R' F' R
U (L' U2 L2 U) (F U' F') (L' U' L' U2 L)
U' (L' U L2 F' L' F) U' (L' U' L U L' U' L)
"U2 (R U R' U') (F' U2 F U) (R U R')
U f D' (R2 U R2' U') (R2 D R2' f')"
U (L' U' L U') (F R U R') (F R' F' R) F'
U F U (R U' R' U) (R U' R2' F') U' F (U R U' F')
U2 (R U R2' F' R) (U R U' R') (L' U' L F)
U L (F U2 F' U) (L' U L U) (L' U' L U) L'
U2 (R' U' R U' R' U2' R2) (U R' U' R' F R F')
U' (F R' F' R) U (R U R' U') (R U R' U') R U' R'
"U2 F' U' (L U L' U) (L U' L' U') F (L' f U f')
U F (R U' R' U') (R' U' R U') (R U R2' F' U F R F')
U' (F R' F' R U R U' R') U' (R' U' R U' R' U R U' R' U2' R)"
"U2 R U R' (f' L' U' L U f) (R' F R F')
U2 (R U R' U) (R' U' F' U F R) U' (R' F R F')"
U' F (R U R' U')2 (R' F' r U R U' r')
U (r U2' R' U' R U' r2) (U' R' F R F' U r)
U' F U (R' F R F) (r U r' U') r' F2 r
U2 (R U R' U2) (F' U' F U') R U' R'
(R' F R U') (R' U R U2) R' U' F' (R U R' U R)
U' (l U2 L' U' L U' l') (F' U' L' U L F)
U (R U2' R' U' R U' R') U' (R U R' F' U2 F R U' R')
U' (L U2 L' U' L U' L') (F' U' L' U L F)
"U2 (L' U' L F U2' F' L' U L2) (U2 L' U' L U' L')
 (F R U' R' U2' R U R' F') (R U2' R' U' R U' R')"
U (f R U R' U' f') (R' U' R U' R' U2' R)
U2 (R U R' U2) (R' U' F R F') (R' U R U2) R U' R'
(R' U' R U' R' U2' R) U (f U R U' R' f')
U' (l F U F' U' l2') (U2 L U L' U l)
(L' U' L U L F' L' S') (U' L' U L f)
F' (L' U L U) (L' U2 L U) (L' U' L U)2 F
(R' F' U' F2 U) (R U' R' F' R)
R2' D' (r U r' D) R U F' U2 F U R
U (R U R' U') (R' U' F R F') (U' R' U2' R)
U2 (r' F' U F) (R U2 R' U') (r U2 R' U' R)
U' (R U R2' F' U' F) (U R2 U2' R')
"(L' U' L U') (L' U L U) (L F' L' F)
 U2 (R' U' R U') (R' U R U) (R f' U' f)"
M' (F R U' R' U' R U2' R' U' F') M
U' (L' U2' L U) (F U F') (L2' D' L U L' D L2)
U' (R' U2' R F) U' (R' U R U) F' (R' F' U F R)
(R' F' r U R U' r') (U' L' U L F)
U (r' U2 R' D') (r U2 r' D) R2 U' R' r
U2 (r U R' U R U2' r') U' (R U2' R' U2 R' F R F')
U (R' F' U' F U R) (L' U' L U L F' L' F)
r' U' (M' U' R U) r2' D' (r U r' D) r2
U' (F R U' R' U2 R U R' F') (L' U' L U L F' L' F)
U' F (R2 D R' U) (R' U' R U) (R2' D' R U' F')
(R' U2' R U R' U R) U (R' U' F U R U' R' F' R)
(R' U' F2 u') (R U2 R' D) (R U' R B)
"(L U2 L' U') (F' L F2 U' L') U' (L' U L U) F'
(F' U' L' U L F) U (F U R U2' R' U R U R' F')"
"(R' F' U' F U' R U R' U R) (F R' F' R U R U' R')
U (R U2' R' U') F' (R U2' R' U' R U' R') U' F (U R U2' R')"
"(L' U' L U' L' U L) (F R U R2' F' R) (U R U' R')
(↑R' U' R' D') R F U' (R U R' U) F' R' D R2"
U2 (R U' L' U R' U' L) U (r' U' R U' R' U2' r)
"U' (↑ L U L' F') (U' L2 U F) (L' U' L U L)
U2 (R U' R' U') (R U R D) (R' U2 R D') R2' U' (R' F R F')"
"U' (F' L' U L) (S' U L' U' L f)
U (R U R' U' R' F R F') (R' U' R' F R F' U R)"
"R' U' F (U2' r U r' U2') F' U' R
U' (L' B' U' B U L) (R U R' U' R' F R F')"
U (R U' R' U') (F U R U' R' F') (R U2' R')
U2 F (R U R' F') (R' F U' F2) U F R
U (F' U' L' U2 L U' L' U' L F) (L F U F' U' L')
(R' F' U F) U (R U R' F') (L' U2 L) F R
R' U2' (R U R' UD') (r U' r' D) (R F' U F)
U2 (R' F' U2' F) (R U2 R' U') (R U2 R' U2' R)
U' (F R U' R' F' L' U L) (R U R' U' R' F R F')
(F R' F' R U R U' R') (F' U' L' U L F)
U (L U' L' U') (F' L U' L2' U L) (F L U2 L')
R' U2' (F R U R' U' F') (R U2 R' F) R' F' R2
(R U R' F') (R U R' U') (R' F R U') (R' F R F')
U' (R' F2 r U r' F) (U' R U' R' U2' R) 
"U (L' U' L2 F' L' F2 U' F') (L' U' L U' L' U2 L)
(F R U R' U' F') (R' F R F' R U2' R' U' F' U' F)"
U' F U' (R2 U R' U) (R U2' R2' U') (R U' R' U') F'
(r U2' R' U' R U' M) (U2' R' U' R U R' U' R U' R')
(R U R' U) (MR U' R' U) (r U' R' U) R U2' R'
U2 (R U R' U R U2' R') U (r' U' r U' R' U M U r)
F' U' (F2 R' F' R2 U R' U') R U' R'
U2 (R U R' U R U2' R') U (r' U' R U' R' U2' r)
U2 (R U2' R' U') F' (R' U' F' U F R) U2 F (U R U2' R')
U↑R2' D' (r U r' D) R' D (r' U' r D') R'
R2' u' (R U' R U) R' u R F' U' F R
U2 (l' U' L U' L' U2 l) U (L' U2 L U2' L F' L' F)
"U' (L F U F' U' L') (R U R' U' R' F R F')
 (f U R U' R' f') U' (R U R' U' R' F R F')"
U2 r U (M U R' U') r2 D (r' U' r D') r2'
"U (F' L' U L U2' L' U' L F) (R U R' U' R' F R F')
(R' U R U') R' U' (R' F' U' F U R2) U R' U' R"
U' F U R' F (R U R' U' R) F' (R' U R U2) F'
(L U2 L' U' L U' L') U' (L U F' U' L' U L F L')
F U (R U' R' U) F' R' F U' F' U R
"(R' U2' R U) (F R' F2' U R) U (R U' R' U') F
(F U R U' R' F') U' (F' U' L' U2 L U' L' U' L F)"
"(L F U F' U L' U' L U' L') (F' L F L' U' L' U L)
U' F (R U R' U) (F' U' F U') (R U' R' U') (R U R' F')"
U2 (L' U R U' L U R') U (r U R' U R U2' r')
(R U R' U R U' R') (F' L' U' L2 F L') (U' L' U L)
U' (l' U2 L U L' U l2') (U L F' L' F U' l')
U2 (R U R' U) (F' U F U2) R U' R'
U2 (r' F2 r2 U' r') F U F (R U2 R' U') F'
U (r' U2' R U R' U r) (F U R U' R' F')
U2 (R U R' F' U2 F R U' R2') (U2' R U R' U R)
U' (R' U' R U' R' U2' R) U (R' U' R' F R F' U R)
U2 (R U R' F' U2 F R U' R') U (R U R' U R U2' R')
U (R' U2' R U R' U R) (F U R U' R' F')
"U' (f' L' U' L U f) (L U L' U L U2 L')
(R' U' F' U F R) U (R U R' U R U2 R')"
U2 (L' U' L U2') (L U F' L' F) (L U' L' U2') L' U L
U2 (R U R' U R U2' R') U2 (R' F' U' F U R)
U (r' F' U' F U r2) (U2' R' U' R U' r')
U (↑R' U' R F) (U R2' U' F') (R U R' U' R')
U (F R U' R') (S U' R U R' f')
"L U F' (U2 l' U' l U2) F U L'
U (R B U B' U' R') (L' U' L U L F' L' F)"
U (R' F' r U) (R U2 r' F2) R U2 R'
U' (F U R U2' R' U R U R' F') (R' F' U' F U R)
U' (L' U L U) (F' U' L' U L F) (L' U2 L)
U' (R' U R U) (R' U2 R U2') R' U2 F' U2 F R
U2 R' U F' U2 (R U R' F') U' F (R U' R' F) U' R
U2 (R U2 R' U') (R U R2' U') F' U F R2 U' R'
"U (F' L' U L F R U' R') (L' U' L U L F' L' F)
(R U R' U) (R' F R2 U R' U') F' U R U R'"
"(F' L F L' U' L' U L) (F U R U' R' F')
U' (F R U' R' U' R U R') (S R U R' U' f')"
"U' (R' U R U) (F R' U R2 U' R') (F' R' U2' R)
U' (R' F R U2') (r U2' r' U2) F' (U' R U R')"
U' (R U2' R2' U') (F' U F) (R U R U2' R')
U (R U' R2' F R F') U (R U R' U' R U R')
"U2 (L' U' L U) (F U2' F' U') (L' U' L)
R' (U2 r' D' r U2 r' D r) R"
U' (R U R' U) (F' L' U' L) (F' L F L') F
U (R U' R' F) (R U R' U') (R U R' U') F' (R' F R F')
"U2 (L' U' L2 F L') (U' L' U L) (R U R' F')
U (R U R' U' R' F R F') (R' U' F U R U' R' F' R)"
U' R' (F' U2' F U') (R U' R' U') (R U R' U') R
"U2 (L U L' U L U2 L2') (U' L U L F' L' F)
 U' (R U R' U R U2' R') (F R U' R' U R U R' F')"
"U (F' L F L') U' (L' U' L U) (L' U' L U) L' U L
 U' R' (F R U R' U' F') (R U' R' U) F' U F R"
U2 F U (R' U' R U') (R' U R U) F' (R f' U' f)
U2 L' U' L (f R U R' U' f') (L F' L' F)
U F' (L' U' L U)2 (L F l' U' L' U l)
(R U R' U' R' F R S) (U R U' R' f')
F (R U' R' U') (R U2' R' U') (R U R' U')2 F'
"(L F U F2' U') (L' U L F L')
U' (r U R' U) (R U' R' U') (r' F R F')"
(R U R U) F R F' U2 R' U' F R' F'
U' (L' U' L U) (L U F' L' F) (U L U2 L')
U2 F' U2 (R' F R U) (R' F' R U) F R U2 R'
F' U' F2 (R U R' U') F2 U2 F
M' (F' L' U L U L' U2 L U F) M
(R U R' U) (R U' R' U') (R' F R F')
U (↓R U2 R' U') (F' U' F) (R2 D R' U' R D' R2')
F U (R U' R' U) (R U2 R' U') F' U' r' F2 r
(r U R' U' r' F R) (U R U' R' F')
U' (R2' F R F') (R U2 R') (F U R U' R' F') U2 R
(L' U' L F) (L' U' L U) (L F' L' U) (L F' L' F)
U' (R U R2' F R F2' U F) (R U R' U R U2' R')
U (L F2' l' U' l F') (U L' U L U2 L')
F (R U' R2' U2') (R U R' U) (R2 U2' R' U') F'
U2 R' U2 (r U R' U') (MR U R' U') (R U R' U R)
R' U2' F' U2' (R U2 R' U' R U' R') F (R U R' U R)
U' (R U' R' U2) (R' U' F R F') (R' U R U') (R' F R F')
F U (F2' L F L2' U' L U) L' U L
(R' U' R U' R' U2' R) U' (r U R' U R U2' r')
U (R U R' F') U2 F U (R U' R' U) (R' F R F') R U2 R'
"U'↑ L2 D (l' U' l D') L D' (l U l' D) L
 U R2 D (r' U' r D') R D' (r U r' D) R"
M'L U' (R U2' r' F) (R U2' R2' F) x M
M' U' x' (R2 U2' R' F') (r U2' R' U) ML'
U r' U2 (R U' R' U) r U2' (r2' F R F') r U' R' U2 r
U2 F (R U2' R2' F2) (R U2 R U2') R' F (r2' F r U' r)
U (L' U2 L F' L F L2' U2 L) (F' L F L' U' L' U L)
(L' U' L U L F' L' F) (L' U2 L2 F' L' F L' U2 L)
U' (R U2' R' F R' F' R2 U2' R') (F R' F' R U R U' R')
(R U R' U' R' F R F') (R U2' R2' F R F' R U2' R')
S (R U R' U') (R' U' R' U R) S'
(R D' F2' R2') (U' r U r' U) (R2 F2' D R')
"(L' D F2 L2) (U l' U' l U') (L2' F2 D' L)
U' F U R' U2' (R2 U R2' U) (R U R' U') F' U F R F'"
(l' D F2 L2) U (L' U2' L U') (L2' F2 D' l)
(r D' F2' R2') U' (R U2 R' U) (R2 F2' D r')
(M' U2 M U2) (M' U M) (U2 M' U2 M)
(L' U L2 F2' U L') F' (L U' F2' L2' U' L)
(R U' R2' F2 U' R) F (R' U F2 R2 U R')
U (F R' F R2 U R' U') F2 U' (r U' r' F)
(R' U' F R' F' R U R) (f U R U' R' f')
(f R U R' U' f') (R' U' R' F R F' U R)
U' F U (R U' R2' F R F') (R U2' R' U') F' U2 r' F r
(R U' R' S) (R' F R f') (R U' B U2' B' R')
R2' S R2 U' S2 U' R2' S R2
(R U R' U') (R' F R2 U R' U' F')
U' F' U2' F U (R U' R' U') (R U' R' U) F' U2' F
(R U R' U' R' F R F') (f' U' L' U L f)
U2 (R U' R' U) M U (R U' R2' D') (R U' R' D) r
F U (R U' R' U)2 (R U2' R' U') (R U R' F')
"(L U F' U' L' U L F L') U2 (L' U' L U' L' U2 L)
(R U2' R2' U') (F' U' F U) (R2 U2' R' U R' U2' R)"
(F R' F' R) U2 (R U' R' U) (R U r' F R' F' r)
F' (U' L' U2 L) S' (U L' U' L) f
U (R U R' U2) (R' F R F) (r U r' F) R U R'
U' (r' U' r U') R' U R F' r' U r F
U' (F' U2' F U') (R U R' U') (R U R' U2') (F R' F' R)
U' (F R' F' R) (U R U R') (F R' F' R) (U' R U' R')
↑R' (F R' F' R U R U' R2') F R F' R
U2 (L' U' L U') (L F' L' F) L' U2 L
U F (R U R' U')2 (R U' R' U2' R U R' F')
U (F' U' L' U L F) (R U2' R' U' R U' R')
U (R B U B' U' R') F (U R U' R')2 F'
U' (L' U' L U' L' U2 L2) (U L F' L' F U' L')
"U' (L F U F' U' L') F' (U' L' U L)2 F
U2 (R U R' U) (F' U F U') (R U' R' U) R U2' R'"
"U2 (F' U' L F' L' F U F) (L' U' L U' L' U2 L)
U' f (U R U' R')2 f' U (F U R U' R' F')"
U (r U R' U) (R U' R' U) (R' F R F') R U2' r'
U R' U2' R2 U2' F R F' U2 (R' U2 R' U2' R)
U (F R U R' U' F') (r U2' R' U' R U' r')
U (f R U R' U' f') (r U2' R' U' R U' r')
U (r U2' R' U' R U' r') (F R' F' r U R U' r')
U (R U' R2' F R F') (R U' R' U2) (R U R' U) R U' R'
(R U2' R' U' R U' R2') (U' F U R U' R' F' R)
U' (F' L' U' L U F) U' (F' U' L' U2 L U L' U' L F)
F (R U' R2' F') U2' (R U R' U) R2 U2' R' F U' F'
U' (↑r' U' r U') (R' U r' D') (R U R' D) R r
U2 (R U R' U) (R U' R' U) (R U' R' F') U F U R U2' R'
U (R' F R F') (r U' r') (R' F R F') (r U2' r')
"U' (F R' F' R) U2' (F R' F' R) (F R' F' R2 U2' R')
U F R' F2 r U' F2' (r U2' r2' F2 R)"
"U (F R' F' U2' R) (U R' U R) (F R' F' R2 U2' R')
U2 (R' F' U' F U R) (r U R' U' r' F R2 U R' U' F')"
U2 (L F' L' U' L U F U' L') (l' U' L U' L' U2 l)
R' U' (F' U F U') (R U R' F) (R U R' U') R' F' R2
"U (L' U' L F) U' (f' U' L' U L S) L' U L
F (R U' R' F) R' F' U2 R U F' R' U R"
U2 (R U2' R2' F R F) (R U2' R' U2) R' F2 R
U (L' U' L U') (L F' L' F) (L' U L U) (L F' L' F)
"U (F' L F L' U') (L2' D' L U L' D L2)
 (R U' R' U') (F' U2' F U) (R U R' U') R U' R'"
(R U R2' F' U' F U R) (U' R U' R')
U F' (R U2' R' U) F' (R' F' R F) (R U R' F)
U' R' U' F' U (L' U2 L U') (L' U2 L F) R
U (F R U R' U') (R U' R' U R U2' R' U' F')
U (R U2' R' U' R U' R') U2 (R' F R U R' U' F' U R)
U2 (↑R' U' R U') (R2' F R F' R) U2' (R' U R U2') R' U2 R
(R U R2' F' U' F R2 U' R') (U R' U R)
"(L' U2 L2 F L') U2 (L F' L' U') F U' L F' L'
 U' (R U R' U) (R U' R' F') U F (R' F R F2) U F"
F U (R U2' R' U2) (r' F R F') (r U' R' U') F'
U (M' U' L' U l) (f' L F L') S
U F' U' F (L F' L' U) L F L'
U' (R' U2' R U2) (R' U' R U2) R' U' (F' U' F U') R
(R' F R U') M' U F' (r U r' U') M
U' (R U2' R' U) (R' U' F U R U' R' F' R) (U' R U' R')
U R U R2' (F' U' F U) (R2 U' R' U') (R' F R F')
(r' F R F') R U M' U2 M U M' U R'
(F R' F' R) U2 (R U' R' U)2 R U2' R'
"U (F' L' U L' D' L U2' L' D L2 U) (L' U' L U F)
F (R U R2' U2' R2 U R2' U) F' (R U R U' R')"
U' (R U' R2' F' U' F U) (R2 U' R' U R U R')
R' U (r U R' U') (F' U' F) RM
U' (R U2' R' U') (S' R U' R' S)
"(R' F' U' F U R) (L U L F' L' F U' L')
 U' (R' U R U) (R' U r U') (R' U R U) r' U R"
U2 r' U' F' U F' r U F (R U R' F')
U S (U2 R U2' R' U' R U' R') S'
U' (l' U2 L U L' U l) f (U R U' R')2 f'
U' (R U2' R' U' R U' R') U2 (R U' R' S' R U R' S)
"U F' U (L U L' U') (L' U' L U) (F L U' L')
U (R' U' R' F R F' U R) U (f U R U' R' f')"
"U2 L U' F (L' U' L U' L' U2 L) U2' F' U L'
U (R' U2' R U R' U R) F (R U R' U')2 F'"
"U' (L' U' L U' L F' L' F L' U2 L2) (F U F' U' L')
U' F U' (R' U R U) F' R' U (R' F R F') U R"
U2 (F' U' F' L F L' U) (L' U' L U F)
U2 (R U R' U R d'·R U' R') (U R U' R' F')
U2 (r U r' U) (R U' R' U2) (R U2' R' U2) r U' r'
(L' U' L U) (L F' L2' U' L U F)
F U' (R' U R U2) R' U' F' (R U R' U) R2 U2' R'
(L' U' L U L F' L' F) (f U R U' R' f')
(R' U R U') M' U' (R' U R2 D) (R' U R D') r'
U' R' F U F' R F U' (R U R' U') F' R' U R
F (U R U2' R') S (U' R U R') f'
(R' U' F U R U' R' F' R) U2' (R U R' U R U2' R')
(F' L F L') U2' (L' U L U') (L' U' l F' L F l')
U' (R U' R' F') U F (R U R' U2) R U2' R'
U' R U R2' F' U' F R2 U' R2' U2' R
U (F' L F L') (U' L' U' L) (F' L F L') (U L' U L)
U' (R U R2' U') (R' F R F') U (R U R U') R'
↑ L (F' L F L' U' L' U L2) F' L' F L'
U2 (R U R' U) (R' F R F') R U2' R'
U' F (R U' R' U2') (R U R' U) (R U' R' U) (R U' R' F')
"U' (F U R U' R' F') (L' U2 L U L' U L)
 U (f R U R' U' f') (R' U2' R U R' U R)"
U2 (F U R U' R' F') U' f (U R U' R')2 f'
U (R U R' U R U2' R2') (U' R' F R F' U R)
U (R' F' U' F U R) F (U R U' R')2 F'
U2 (F U R' F R F' U' F') (R U R' U R U2' R')
"U' (l' U' L U') (L' U L U') (L F' L' F) L' U2 l
 F (R U' R' U) (R U R' U R U2' R') U' (R U R' F')"
U F (R U' R' F') (r' F' r U r' F U') (R U' R' U2') r
"U' (F' L' U' L U F) (l' U2 L U L' U l)
 U2 (R' F' U' F U R) U' (r' U2' R U R' U r)"
U' (f' L' U' L U f) (l' U2 L U L' U l)
U' (l' U2 L U L' U l) (F' L F l' U' L' U l)
U' (L' U L2 F' L' F) (L' U L U2') (L' U' L U') L' U L
"(L' U2 L U L' U L2) (U F' U' L' U L F L')
(F R U' R' U' R U R' F') (r U R' U R U2' r')"
U (F R U R' U' F') U (F U R U2' R' U' R U R' F')
U (r' U r U2) (M U R' U') (r U' R' U') (F' U' F R)
U (↑ l U l' U) (L U' l D) (L' U' L D') L' l'
(R' U' R U') (R' U R U') R' U' F' U' F (R U R' U2') R
"U' (L F' L' F) (l' U l) (L F' L' F) (l' U2 l)
 U (F U R U R' F' U F R U R' U) (R U R' U' F')"
"U (F' L F L') U2 (F' L F L') (F' L F L2' U2 L)
 F (R U' R' U') (R U R' U) (R' F R F') (R U' R' F')"
(R U' R2' U') F' U F (R U' R' F) R F' R U2 R'
U2 (R' F R U R' U' F' U R) (r U R' U R U2' r')
"U2 (R' F R U R' U' F' U R) (r U r' U R U' M' U' r')
U' (R U2 R' U') (R U R' U) F' U F (R U' R' U) R U' R'"
U' F U' (R U' R' U2') (R U' R' U2') (R U2 R' F')
U' (M' U R U' r') (f R' F' R) S'
U' (F U F') (R' F R U') (R' F' R)
U2↑R' U (F' U F U) (R U2' R' U) (R U2' R' U2) R
(L F' L' U) M' U' F (l' U' l U) M
"U (L' U2 L U') (L U F' U' L' U L F L') (U L' U L)
U2 R U2' R2' U' F' U F R U (R U' R' U) (R U2' R')"
(r U' r' F) U F (R U2' R' U) (R U R' F')
(M U' M' U2 M U') (r U' r' F R' F' r)
"(F' L F L') U2' (L' U L U')2 L' U2 L
 U (R U R' U) (R U' R' U) (R U' R') (F' U F) (R U' R')"
"U' (↓F R U' R D R' U2 R D' R2' U') (R U R' U' F')
(R' U R U') (R' U R U2') (R2' F R F' R) U R' U R"
"U (L' U L2 F U F' U') (L2' U L U' L' U' L)
(F R U' R' U2' R U R' F') (R U' L' U R' U' L)"
L U' (l' U' L U) (F U F') L'M
U' (R U R' F') U (f U R U' R' S') R U' R'
U2 (L' U2 L2 F' L' F') (L' U2 L U2') L F2' L'
U' (R U R' U) (R' F R F') (R U' R' U') (R' F R F')
U' (F R' F' R U) (R2 D R' U' R D' R2')
"(L' U' L2 F U F' U' L') (U L' U L)
U2 (R' U' R U) (F R U R' U' F') R' U R"
U' F (L' U2 L U') F (L F L' F') (L' U' L F')
U2 (F R' F' R) U2 (R' F R F') (R U' R' U) R U2' R'
"U' (F' L' U' L U) (L' U L U' L' U2 L U F)
U (R U2 R' U') (F' U F U) (R U' R' U) R U2' R'"
"U' (L' U2 L U L' U L) U2' (L F' L' U' L U F U' L')
U r' D' (R U R' D) (R2 U R' U2') R U R'M'"
U2 (↑ L U L' U) (L2 F' L' F L') U2 (L U' L' U2) L U2' L'
"(L' U' L2 F U F' L2' U L) (U' L U' L')
 U' (r U R' U) (R' F R F') (R U' R' U') (r' F R F')"
(R U2' R2' F' R) U2' (R' F R U) F' U R' F R
U' (R' U2' R U) (S' R' U R S)
(L F U F' U' L') (R' U' R' F R F' U R)
(r U R' U) (R U' R' U') M U R U' R'
U S U2 (R' U2' R U R' U R) S'
U f (U R U' R')2 f' (R U2' R' U' R U' R')
U' F U' (R U2 R' U) (R U R' U') (R U2' R' U2) F'
U' F U' (R' U' R U) (R U R' U') (F' R' U R)
U2 R' U F' (R U R' U R U2' R') U2 F U' R
U (R U R' U R' F R F' R U2' R2') (F' U' F U R)
U2 (F U F R' F' R U') (R U R' U' F')
U2 (L' U' L U' L' d· L' U L) (U' L' U L F)
(r' U' r U') (R' U R U2') (R' U2 R U2') r' U r
U2 R2' F (R U R U') (R' F' R U') (R' F' U F) R
(l' U' L U) (l F' L2' U L U') (L' U' L F)
(F' L' U' L U F) (L' U R U' L U R')
U (R' F' U' F U R) (r U R' U' r' F R F')
U (r U R' U) (R' F R F') U2 (r' F R F')
U F U (R U' R2' F R F') U (F R' F' R2) U R' F'
"U' L U F' (U' L' U L) F' l' U' l F' L'
U2 F U R2 D (r' U2 r D') (R' U R' F')"
U' (R' U' R U') (R U R' U') (R' U2' F R F')
U' (L' U2 L U) (L' U' L U) (F U' F' U') (L' U2 L)
(R U2' R' U) (R' F' U' F U) (R2 U' R' U') R U' R'
U2 R' U F' U F (R U' R' U') (R U' R' F') U F R
F U (R' U' R U) (R U' R' F') (U2 R' U2' R)
"(l U2 L' U' L U' l') (f' U' L' U L f)
U2 (R' F R2 U R' F') R' F R2 U' R2' F' R"
U2 F (R U' R' F') (r U' r' F2) U' F'
U2 (R U2 R' U') (R' F R F) (r U r' U) F
"U2 (L U L' U L U2 L2') (U' L F U2' F' L' U L)
 (R U R' U R U2' R') (F R U' R' U2' R U R' F')"
U' (l' U' L U' L' U2 l2) (U F U' F' l')
U2 (R U2' R' U' R U' R') (F U R U' R' F')
U' (R' F' U' F U R2) U2' (R' U' R U' R')
U2 R U' (F' U' F U') (R U' R' U') F R' F'
U (R' U' R' F R F' U R) U (R' U2' R U R' U R)
U (R' U' R U') (R U2' R2' U' R2 U' R2') (F' U F R)
"U (M U' l F U F' U' l2') (U2 L U L' U L)
U2 (R U2' R2' U' R2 U' R' U R' U R) (F R U R' U' F')"
U2 (F R U R' U' F') (R' U' R U' R' U2' R)
(↓r U R U' r') (F U R' U' F')
"U F U (R U2' R' U) (R U B U' B' U R') F'
U F U (R U2' R' U) (R U R' U) (R' F R F') U' F'"
U' R' U' R (F R' F' U' R) (U R U' R2' U2' R)
(f' L F L') (U' L' U L) S
M F' L F l2' (L U' L' U) l
"(F U F') (R U2' R' U2') (R' F R2 U2' R' U') F'
U' (R U R' U R U2' R') U2 (F R U' R' U R U2' R' U' F')"
"U2 (r U R' U2') (r' F R U) (R U' R' U) (F R U' R' F')
(↓R U2 R' U') (R2 U' R' F U) (R2 U' F' R' U R)"
"U L' U (L2 U F U' F' L') (U L' U2 L)
 U' (R' U R U) (F U R U' R' F') R' U2' R"
U2 (R U' R' F') R' U' R F U (R U R' U') R' U R
(R U2' R2' U' F' U F R2 U' R') U' (R' U' F' U F R)
"U2 (F R' F' r U R U' r') F (U R U' R')2 F'
 U2 R2 U2' (R' U R U') R U2' R F' U2 F R"
U2 F R U2' R2' U' F' U F (R U' R U') R' F'
U2 (L' U' L U L F' L' F) (R U R' U R U2' R')
U' (R' U' R U') R2 U2' (R U R' U) R U (F' U F U) R
"(F R U' R' U) (f R U R' U' f') (R U R' F')
U2 F U R U' F' (r U R2' U) R U2 r'"
(R' U' R) (f R f') (R' U' R U) R' U R
(R' U R' F') U' F (R U R U') R' U' R' U R2
U (F' L F L' U2' L' U2 L2) (F U F' U' L')
U2 (R' U' R U') (M' U R' U') r' D' (r U2 r' D) R2
U' (L U2 L2' U' L U') (L' U L U) (L U' F' L' F)
(l U L' U L U2 l') (L' U' L U L F' L' F)
"U (F R' F' R U2 R U2' R') U F' (U' L' U L)2 F
U↑R' U2 (R U' R' U) (R U R2' F' U' F) (U R U R)"
U2 (R U R' U R U2' R2') (F R F' U R U R' F' U2 F)
(L F' L' U) L F' U· (L' U L U') (L F L' U') F L'
U' F (R U2 R' F') U F (R U R' U) F'
U2 L (F' L' U' L U F) U' L'
F (R U R' U2) (R' U2' R U) F' (U' R' U2' R)
U2 (r U R' U' r' F R) (S U R U' R' f')
F (R U R' U')2 (R U' R' U' R U R' F')
S' U' (F R' F' R U R U' R') S
U' (L' U2 L U2') (L U F' L' F) L U' L'
"U' (F U' F' U2) (F' L F L') U' (L' U' L U L' U2 L)
U R' U2' (F' U F U) (R U2 R' U) (R U R' U2' R)"
"(L' U L F) (l U2 L' U' L U' l') U' F'
U2 (R U R' F') U' (R' U2' R F) U' (R' U' F R F')"
(F R U R' U') (R F' U2 R' U' R U' r U R' U' r')
U2 F' U' F R' D' (r U r' D) R
(R U R' U' R' F R F') (L' U2' L U L' U L)
U (L' U L F) (R U R' U') (R U' R' F') L' U' L
(F R' F' R U2 R U2' R2') (F R U R' U' F' U R)
U2 (R U R' U') F2 (r U r' F) (U' R U R')
U (L U2 L' U' L U') (F l' U l F2' L')
U' (R U R' U) (R U' R2' F R F2') U F
"U (L U L' U L U2) (F2' l' U' l F' L')
 U' (R U R' U R U2' R') U2 (r U2' R' U' R U' r')"
U (r U r' F) U F2 (L' U' L U') R' F' R
U2 (r' U' M' U' R U r' U r) U' (R U2' R' U' R U' R')
(R' F R F') U (R U R' U2) (R U2' R' U') (F' U' F)
(F' L' U' L U) (L' U L2 U2 L' U' L U' L2' U' L F)
U (R' U2' R U) (R' U' R U) R' (F R' F' R) F' U F R
(R' U2' R U R' U) (M U2' R U R' U' R U R' U r)
(r' U' R U) (R' F' r U2) (R' U' r U') r' F R
"(F' L' U L U') (f' L' U' L U f) (L' U' L F)
U2 (R U R' F') U2 (R' U' F' U F R) U F R U' R'"
U2 (R U R') (F' U' F) (R U R' U') R U' R'
U2 (R U R' U' R' F R F') (L' U' L U' L' U2 L)
U' (F R' F' R U2 R U2' R2') (F' U' F U R)
U' F U' (R' U' R U) (R U R' U') (R' F' U F) R F'
(r' U' R U' R' U2' r) (R U R' U' R' F R F')
U2 R2' U2' (R U' R' U') (R' F R F') (R U2' R' U2) R2
U (R' U2' R2 U R' U) (R U' R' U') (R' U F R F')
"U' (F' L F L' U2' L' U2 L) U' F (U R U' R')2 F'
U2 (R' F R F' U2 F' U2 F2) U (R U' R' U) (R U' R' F')"
"U2 (L' U' L U' L' U2 L2) (F' L' F U' L' U' L F U2' F')
 (R' U' R U' R' U2) (R' U R' F' U2 F R U' R' U' R')"
(R' F R U') R' F U'·(R U' R' U) (R' F' R U) F' R
"(r' U2' R U R' U r) (f U R U' R' f')
U2 (R' F2 r U r' F R) (F R U R' U' F')"
U2 (R' F R' F' R2) U' (R' F' U' F R)
U2 (r' F2 r U) (r U' r' F') (R' F' R U') F'
U2 (R' U' R U' R' U2' R2) (U R' F' U2 F R U' R')
U (r U R' U R U2' r2') (U' F' U F r)
(F R U R' U' F') (R U R' U R U2' R')
U' (R B U B' U') (R2' U2' R U R' U R)
(R' U2' R U) R' F' U' (R U R' U R U2' R') F R
U' (L U L F' L' F U' L') U' (L U2 L' U' L U' L')
"U (R U R' U) (R' U2' R2 U R2' U R2) (B U' B' R')
U F (R U R' U')2 F' (R U2' R2' F R F' R U2' R')"
U2 (F' L' U' L U F) (L U L' U L U2 L')
U' (M U r' F' U' F U r2) (U2' R' U' R U' R')
R' F' U2 F (R U' R' F') U' F U' R
U2 R' (F R U R' U' F') U R
U' R2' D' (R U2 R' D) R U2 (F' U' F U) R
"U2 (l' U' L U l F' L') (S' U' L' U L f)
 U F U (R U' R' U') (R' F R F') (R U2' R' U') F'"
"F' (L' U' L U)2 (L' U L U L' U' L F)
 (F R U R' U') (R' U' R2 U' R2' U2' R2 U' R' F')"
S U (F' L F L' U' L' U L) S'
U (R U2' R' U2) (R' U' F R F') R' U R
U (F' U F U2') (F R' F' R) U (R U R' U' R U2' R')
(R U' R' F') (r' U2' R U R' U r) U F
U' (L' U R U' L U R') F (U R U' R')2 F'
f R f'·R D (r' U' r D') R'
(L' U' L U L F' L' F) (R U2' R' U' R U' R')
U R' F' U2 (R' U2' R U) R' F U F' R F U' R
(r U R' U') (r' F R2 U' R' U) (R U R' F')
(F R U R' U' F') (R U' L' U R' U' L)
"U' (L F U F' U' L') (l' U' L U l F' L' F)
U2 F (R U R' U2) (L' U R U' L U R') F'"
"U' (l' U' L U') (L F' L' F) U2' (l F' L' F)
 U' (R' F' U' F) (R' F R U) (R U' R' F') R"
U' F (R2 U R' U) (R2' F R F' R2) U2' R2 F'
U R' U' F (U R U' R') F r U r' F R
(R U' R' U) (R U R' U') (F' U F U') R U R'
U (R U2' R' U') (R U R' U') (F' U F U) (R U2' R')
U2 R' U2' R (F R U R' U' F') U' (R' U R U) R' U R
U' (R' F' U' F U R) (F U R U2' R' U R U R' F')
U2 (r' U2 r U) r' R' D' (r U r' D) R2 U M'
"(↓ l' U' L' U l) (F' U' L U F)
U2 (R' U' R U) (R U R' U') (R' U F R F')"
U' F' U' (L' U2 L U') (L' U' B' U B U' L) F
U L U L' (F' L F U L') (U' L' U L2 U2 L')
(f R' F' R) (U R U' R') S'
M F R' F' r2 (R' U R U') r'
"(F' U' F) (L' U2 L U2) (L F' L2' U2 L U) F
U' (M' U M U) (R U R' F' U' F U r U2' r')"
"U2 (l' U' L U2) (l F' L' U') (L' U L U') (F' L' U L F)
(↓ L' U2' L U) (L2' U L F' U') (L2' U F L U' L')"
U' R U' (R2' U' F' U F R) (U' R U2' R')
R' U2' R F U R' U' F' U2 (R U R U') R'
U' (R' F' R U2) R' F U2 F' U' (R U R' F) U2 R
"U2 (F' L F l' U' L' U l) F' (U' L' U L)2 F
 R2' U2' (R U' R' U) R' U2 R' y (R U2 R' F')"
U R' U' (R' U2' R2 U) (R2' F R F' R') U R U R
U2 (R U' R' F') (L' U' L U') (L' U L) (F R U R')
(F' L F L' U2' L' U2 L2) (F' L' U' L U F U' L')
U' (R U' R' U) F' (r U' r' F2) U R U' R'
U' (R' U2' R U R' U) (F' r U' r' F2 R)
U (L' U' L U') (L' U L2 F' L' F2) U' F'
U' (R' U' R U' R' U2') (F2 r U r' F R)
U' (R' F' R F') U' F2 (R U R' U) r U r'
(r U M U R' U' r U' r') U (R' U2' R U R' U R)
(R U R' F') (R U2' R' U' R U' R') U2' F (U R U2' R')
(F R U R' U') (R U' R2' U2' R U R' U R2 U R' F')
U2 (R U R' U) (MR U' R' U) (R U' R' U) r U2' R'
U2 (R U R' U R U' R' U R U2') (M' U R' U R U2' r')
"""
update_all("CUBEROOT", CUBEROOT_ALLL)

CUBE_EXPLORE = """
U2 B' R' F' U2 F U2 R2 B2 L' B R' B2 L  
R U' R' F' L2 U2 F' L' F U2 L2 U F 
U' B U L2 U2 B L' B' U2 L2 B' R' U' R 
U2 L U F' U' L' U L' F U2 F U2 F' L  
L F U F' U' L' F U R U' R' F' 
U' B' U L F2 D R2 D' F2 L' U2 B  
U2 R B2 U B' U' D B D' B D B2 D' R' 
U2 B L U L' U' B' L U F U' F' L' 
F2 R' D F D' F' R D R2 D R2 D2 F2 
U' L' U B2 U' L2 F' L2 B' L2 F L2 U B2 L 
B L2 F' B R' B' L2 B R B2 L F L'
U2 B U' F U' B2 R B2 U2 B2 R' B U F'  
U F' U' F U2 R B2 L' B' L U2 B' U' R' 
U F B' D' R2 D B2 U' B' U F'  
R U2 R2 F2 L D2 R' D2 R2 F2 L'  
U L U L' U' L F2 R' F' R2 U2 R' F' L'  
F' D' L' D F' B2 R F2 B U' F2 R' F2 B  
U R' F' D2 B' L U2 F' L2 F D2 F' R' F2  
U R' U R B L2 U2 B L B' U2 L2 U' B'  
U' R' U' F2 U2 R' F R U2 F2 R B U B' 
L F' L' F U R' D F2 U' F U F2 D' R 
U2 L U2 R F R' U2 R F' L' B U B' U' R' 
F R2 U F' R' U L2 D' B D' R' D2 R L2  
R2 D' L D R2 U F U' F' R' D' L' D R  
"""
update_all("CUBE_EXPLORE", CUBE_EXPLORE)