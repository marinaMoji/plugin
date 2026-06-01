# Sources and further reading

## Primary (cited in planning)

| Source | Author / site | Use for this project |
|--------|---------------|----------------------|
| [コンピューター上の漢文訓読表記法に関する現状と課題](https://k-rain.repo.nii.ac.jp/record/2000213) (PDF: `chugokugakkaiho_065_007.pdf`) | 篠原泰彦 (2024) | Survey of macros; critique of 訓点マクロ; recommends 睡人亭 for Word |
| [Wordで漢文入力 — 送り仮名とレ点](https://www.shuiren.org/chuden/toyoshi/kanbun/01.htm) | 睡人亭 (山田崇仁) | Subscript kaeriten; field-code trick for kaeriten on ruby line |
| [Wordで漢文を打つ方法・その1](https://furukoto.hateblo.jp/entry/2021/05/04/000335) | ふること | EQ field structure for okurigana + レ点 |
| [Wordで漢文入力 — 再読文字](https://www.shuiren.org/chuden/toyoshi/kanbun/03.htm) | 睡人亭 | Nested EQ / field codes for 再読 |
| [漢文エディタ](https://www2s.biglobe.ne.jp/~Taiju/leaf/tjsoft05_kanbun.htm) | 大島太柔 | Tag workflow `[レ]` → export; Unicode U+3190+ discovery |
| marinaMoji `kaeriten.tsv` | this repo | Authoritative IME shortcut → code point table |

## Secondary

| Source | Notes |
|--------|--------|
| 千田大介, 「訓点を打つ」 / 「訓点文を作る」 (*電脳中国学* / *電脳中国学入門*) | Original 訓点マクロ documentation (CD-ROM); tag + 「訓点」 button workflow |
| 山田崇仁, 「一太郎で訓点付き漢文を作成する」 (*漢字文献情報処理研究* 13) | Compares Word effort vs 一太郎 文字パレット |
| 師茂樹, 「漢文のマークアップ　現状と課題」 | LaTeX markup (`\kundoku`) — long-term structured corpus angle |
| [Unicode chart Kanbun U+3190](https://www.unicode.org/charts/PDF/U3190.pdf) | Official character names |
| [HDIC: LuaTeX kunten / sfkanbun](https://shikeda.github.io/docs/krm/06-typesetting/06-04-vscode-texlive/) | When Office output is not enough |

## Software mentioned in 篠原 (2024) — not all maintained

- 漢文快くん (font + `.dot` macros)
- 漢文便利だな~ (Word)
- 漢文エディタ (Excel → Word)
- 漢文ツール (objects in Word)
- 訓点マクロ (Word, 千田大介)
- 一太郎 文字パレット「漢文」

## LibreOffice technical

| Topic | Starting point |
|-------|----------------|
| Frame-based kaeriten (project) | [LIBREOFFICE_FRAMES.md](LIBREOFFICE_FRAMES.md) |
| Python / UNO extension | `.oxt`; `XTextCursor`, text frames anchored as character |
| Ruby API | Tested — **not** used for kaeriten (furigana-like placement) |
| Legacy macros path | `~/.config/libreoffice/4/user/Scripts/python/` (superseded by `.oxt` plan) |
