# Export ZIP AI Printables

## Tags
#ai-printables
#kdp
#plr
#warriorplus
#prompt-pack
#canva-printable
#coloring-book
#journal
#kids-worksheet
#etsy-printable
#export-zip

## Purpose
??ng g?i s?n ph?m th?nh ZIP th?t.

## When To Use
User h?i export ZIP, ??ng g?i, t?o file zip, manifest, placeholder check.

## Input Needed
Product folder, export folder, product name, required files.

## Data Source
M?c ??nh d?ng d? li?u t?:
G:\Documents\warriorplus MMO\Agent PLR Saas\input_files\AI Printables KDP Promt Skill

B?t bu?c kh?ng b? qu?n th? m?c recovered:
G:\Documents\warriorplus MMO\Agent PLR Saas\input_files\AI Printables KDP Promt Skill\_RECOVERED_3500_20260522

Khi ??c d? li?u, lu?n ghi r? `Data used` g?m file/folder c? th? ?? d?ng. N?u file n?n qu? l?n ch?a gi?i n?n/??c ???c, ghi r? `SKIPPED` v? l? do.

## Steps
- Qu?t product folder v? t?o manifest.
- Qu?t placeholder quan tr?ng: [your name], [your website], [support email], [download link], [payment link], [affiliate link], [JV link], [launch date], [insert product name], [company name].
- N?u c?n placeholder quan tr?ng th? Public Launch Gate = FAIL.
- T?o export/product_pack.zip th?t.
- T?o ZIP_PATH.txt, EXPORT_LOG.md, FILE_MANIFEST.md, PLACEHOLDER_CHECK.md.

## Output Format
export/product_pack.zip
export/ZIP_PATH.txt
export/EXPORT_LOG.md
export/FILE_MANIFEST.md
export/PLACEHOLDER_CHECK.md

## Quality Rules
- N?u ZIP kh?ng t?n t?i th? Export ZIP = FAIL.
- N?u c?n placeholder quan tr?ng th? Public Launch Gate = FAIL.

## Failure Conditions
- ZIP kh?ng t?n t?i.
- Kh?ng c? manifest ho?c placeholder check.

## Auto-Update Rule
Khi user feedback ki?u "l?n sau l?m th? n?y", "c?i n?y sai", "thi?u ph?n n?y", "fix l?i", ho?c "ch?m k? h?n":
1. X?c ??nh skill li?n quan.
2. Patch ch?nh file markdown n?y.
3. T?ng `Version` theo semver patch, v? d? v1.0 -> v1.1.
4. Ghi thay ??i v?o `_changelog.md`.
5. Ghi request, skill, l?i, v? fix v?o `_usage_log.md`.
N?u c?ng l?i x?y ra 2 l?n, b?t bu?c update skill tr??c khi tr? l?i ti?p.

## Example Trigger
#ai-printables #export-zip ??ng g?i s?n ph?m hi?n t?i th?nh ZIP v? t?o manifest.

## Version
v1.0
