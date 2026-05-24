# Buyer Test AI Printables

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
#buyer-test

## Purpose
Gi? l?m buyer m?i mua pack gi? $17-$27.

## When To Use
User h?i test nh? buyer, ng??i mua c? hi?u kh?ng, pack n?y ??ng ti?n kh?ng.

## Input Needed
Product folder/files, price, buyer profile, delivery page n?u c?.

## Data Source
M?c ??nh d?ng d? li?u t?:
G:\Documents\warriorplus MMO\Agent PLR Saas\input_files\AI Printables KDP Promt Skill

B?t bu?c kh?ng b? qu?n th? m?c recovered:
G:\Documents\warriorplus MMO\Agent PLR Saas\input_files\AI Printables KDP Promt Skill\_RECOVERED_3500_20260522

Khi ??c d? li?u, lu?n ghi r? `Data used` g?m file/folder c? th? ?? d?ng. N?u file n?n qu? l?n ch?a gi?i n?n/??c ???c, ghi r? `SKIPPED` v? l? do.

## Steps
- ??ng vai buyer m?i, kh?ng bi?t g? tr??c.
- M? Start Here tr??c; n?u kh?ng c? Start Here th? FAIL.
- Ki?m tra c? t?o output ??u ti?n trong 10 ph?t kh?ng.
- Ghi ?i?m stuck, valuable, generic, refund reason.
- N?u score d??i 8 th? ch?a ???c launch.

## Output Format
BUYER TEST REPORT
- Buyer profile:
- Price paid:
- First impression:
- Do I know what to open first?
- Can I create first output in 10 minutes?
- Where did I get stuck?
- What felt valuable?
- What felt generic?
- Would I refund?
- Refund reason:
- Buyer satisfaction score:
- Fix required:

## Quality Rules
- N?u kh?ng c? Start Here th? FAIL.
- N?u buyer score d??i 8 th? ch?a ???c launch.

## Failure Conditions
- Kh?ng c? buyer score.
- Kh?ng n?u refund reason.

## Auto-Update Rule
Khi user feedback ki?u "l?n sau l?m th? n?y", "c?i n?y sai", "thi?u ph?n n?y", "fix l?i", ho?c "ch?m k? h?n":
1. X?c ??nh skill li?n quan.
2. Patch ch?nh file markdown n?y.
3. T?ng `Version` theo semver patch, v? d? v1.0 -> v1.1.
4. Ghi thay ??i v?o `_changelog.md`.
5. Ghi request, skill, l?i, v? fix v?o `_usage_log.md`.
N?u c?ng l?i x?y ra 2 l?n, b?t bu?c update skill tr??c khi tr? l?i ti?p.

## Example Trigger
#ai-printables #buyer-test Test pack n?y nh? buyer m?i mua gi? $17.

## Version
v1.0
