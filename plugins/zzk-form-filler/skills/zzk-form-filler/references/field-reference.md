# ZZK form – PDF field reference

Template: fillable "VZOR ZZK" PDF (form 19 09 01 853, 7 pages, 168 AcroForm fields).
Dates are DD.MM.YYYY. "Code" fields take a 3-letter country code (PHL, CZE, …).

## Template defaults
The template may carry pre-filled values (application type checkboxes, vacancy number, employer block C,
Czech residence address E, anticipated arrival date, attachments, place and date of application).
These are kept unless the mapping fills or overrides them. Inspect the actual template to list them.

## Page 1 – A. Application, B. Applicant
| Field | Meaning |
|---|---|
| A_permit, A_02_renewal | checkbox: new permit / renewal |
| A_03_work_position_in_registry, A_04_work_permit_issued, A_05_work_permit_applied, A_06_free_access | checkbox: type of work position |
| vacancy_number | vacancy number |
| surname, first_name, other_names | applicant names (other_names box is on the "Other names" line) |
| telephone, e-mail | contact |
| date_of_birth, country_of_birth (code), place_of_birth | birth |

## Page 2 – B. (cont.), C. Employment, D. Last employment, E. CZ residence, G. Last residence abroad
| Field | Meaning |
|---|---|
| C_M / C_F | checkbox: male / female |
| nationality | nationality code |
| C_S / C_Ma / C_D / C_W | checkbox: single / married / divorced / widowed |
| education | highest education |
| ocupation | applicant occupation (note spelling) |
| Employer_in_CZ, IČO, employers_business_address, Position_in_CZ, Place_of_employment, C_9, C_9_a, C_10 | C. requested employment no. 1 |
| last_employment_before_arrival | D. employer |
| last_position | D. position |
| last_employment_address / D_4 | D. municipality / municipal district |
| D_5 / D_5_a / D_6 | D. street / No. / post code |
| l_e_country_code | D. country code |
| CZ_res_municipality / CZ_res_municipal_district | E. municipality / district |
| CZ_res_street / CZ_res_number / CZ_res_post_code | E. street / No. / post code |
| last_address_abroad / G_2 | G. municipality / district |
| G_3 / G_4 / G_5 | G. street / No. / post code |
| last_residence_country_code | G. country code |
(Section F – delivery address – has no fields.)

## Page 3 – H. Previous stay, I. Arrival, J. Spouse, K. Children
| Field | Meaning |
|---|---|
| H_1 / H_2 / H_3 | previous stay from / until / purpose and place |
| anticipated_arrival_CZ | anticipated arrival date |
| passport_number, psprt_issued_country_code, psprt_valid_till | travel document |
| spouse_surname, spouse_first_name(s), spouse_other_names | spouse names |
| J_4 | spouse all previous surnames |
| spouse_date_of_birth, spouse_country_of_birth_code, spouse_nationality | spouse birth / nationality |
| J_8 | spouse place of birth |
| J_9 | spouse occupation |
| J_10 / J_11 | spouse residence municipality / district |
| J_12 / J_13 / J_14 | spouse street / No. / post code |
| J_15 | spouse residence country code |

Children – 4 blocks of 8 fields. Child n uses K_(8n-7) … K_(8n):
| Offset | Child 1 | Child 2 | Child 3 | Child 4 | Meaning |
|---|---|---|---|---|---|
| +1 | K_1 | K_9 | K_17 | K_25 | surname |
| +2 | K_2 | K_10 | K_18 | K_26 | first name(s) |
| +3 | K_3 | K_11 | K_19 | K_27 | other names |
| +4 | K_4 | K_12 | K_20 | K_28 | date of birth |
| +5 | K_5 | K_13 | K_21 | K_29 | place of birth |
| +6 | K_6 | K_14 | K_22 | K_30 | nationality code |
| +7 | K_7 | K_15 | K_23 | K_31 | occupation |
| +8 | K_8 | K_16 | K_24 | K_32 | residence address (full, one line) |

## Page 4 – L. Father, M. Mother, N. Siblings
| Father | Mother | Meaning |
|---|---|---|
| L_1 | M_1 | surname |
| L_2 | M_2 | first name(s) |
| L_3 | M_3 | other names |
| L_4 | M_4 | date of birth |
| L_5 | M_5 | nationality code |
| L_6 | M_6 | occupation |
| L_7 | M_6_a | residence municipality |
| L_8 | M_7 | municipal district |
| L_8a | M_7_a | street |
| L_9 | M_8 | No. |
| L_10 | M_8a | post code |
| L_11 | M_9 | country code |

Siblings – same 8-field layout as children: sibling n uses N_(8n-7) … N_(8n)
(surname, first name, other names, DOB, place of birth, nationality code, occupation, full address).
**Quirk:** sibling 4 place of birth is named `M_29` (not N_29).

## Page 5
| Field | Meaning |
|---|---|
| attachments | list of attachments (lines separated by \r) |
| additional_information | free text |
| place, date_of_application | place and date of signature |

## Technical notes
- Some widgets store `/Rect` as indirect objects – resolve them before letting pypdf generate appearances (script does this).
- Do NOT set NeedAppearances=true: viewers then redraw the template's fields and drop Czech diacritics (Ě, Ř, Č).
- Each output ≈ 6 MB, ~4 s per worker.
