# 原 ERP 数据库结构目录

此文件由 `tools/inspect_source_schema.py` 从系统元数据生成；未读取业务记录。

- 对象总数：457
- 候选对象：329
- 外键约束：430

## 候选对象

### `dbo.ac_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ac_code` | varchar(15) | NO |
| 2 | `ac_upper_ac` | varchar(15) | NO |
| 3 | `ac_name` | varchar(50) | NO |
| 4 | `ac_type` | int(10,0) | NO |
| 5 | `ac_category` | int(10,0) | NO |
| 6 | `ac_d_c` | varchar(1) | NO |
| 7 | `ac_curr` | varchar(4) | NO |
| 8 | `ac_dept_req` | bit | NO |
| 9 | `ac_analy1_src` | varchar(1) | NO |
| 10 | `ac_analy1_ctrl` | varchar(1) | NO |
| 11 | `ac_analy2_src` | varchar(1) | NO |
| 12 | `ac_analy2_ctrl` | varchar(1) | NO |
| 13 | `ac_analy3_src` | varchar(1) | NO |
| 14 | `ac_analy3_ctrl` | varchar(1) | NO |
| 15 | `ac_analy4_src` | varchar(1) | NO |
| 16 | `ac_analy4_ctrl` | varchar(1) | NO |
| 17 | `ac_valid` | bit | NO |
| 18 | `ac_qty_control` | bit | NO |
| 19 | `ac_unit` | varchar(4) | NO |
| 20 | `ac_trans` | bit | NO |
| 21 | `ac_inventory` | bit | NO |
| 22 | `ac_daily` | bit | NO |
| 23 | `ac_settle` | bit | NO |
| 24 | `ac_bank_ac` | bit | NO |
| 25 | `ac_cash_ac` | bit | NO |
| 26 | `ac_cashflow` | bit | NO |
| 27 | `ac_cashflow_item` | varchar(4) | NO |
| 28 | `ac_level` | int(10,0) | NO |
| 29 | `ac_crt_by` | varchar(12) | NO |
| 30 | `ac_crt_date` | datetime | NO |
| 31 | `ac_mod_times` | int(10,0) | NO |
| 32 | `ac_mod_by` | varchar(12) | NO |
| 33 | `ac_mod_date` | datetime | NO |
| 34 | `ac_char1` | varchar(255) | NO |
| 35 | `ac_char2` | varchar(255) | NO |
| 36 | `ac_char3` | varchar(255) | NO |
| 37 | `ac_char4` | varchar(255) | NO |
| 38 | `ac_char5` | varchar(255) | NO |
| 39 | `ac_char6` | varchar(255) | NO |
| 40 | `ac_qty1` | decimal(19,8) | NO |
| 41 | `ac_qty2` | decimal(19,8) | NO |
| 42 | `ac_multi_curr` | bit | NO |
| 43 | `ac_view_perm` | varchar(255) | NO |
| 44 | `ac_cashflow_item_c` | varchar(4) | NO |

### `dbo.acg_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acg_nbr` | varchar(15) | NO |
| 2 | `acg_date` | datetime | NO |
| 3 | `acg_cust` | varchar(8) | NO |
| 4 | `acg_curr` | varchar(4) | NO |
| 5 | `acg_vat_rate` | decimal(19,8) | NO |
| 6 | `acg_rmks` | varchar(255) | NO |
| 7 | `acg_site` | varchar(8) | NO |
| 8 | `acg_wf_status` | varchar(1) | NO |
| 9 | `acg_prog_code` | varchar(12) | NO |
| 10 | `acg_crt_by` | varchar(12) | NO |
| 11 | `acg_crt_date` | datetime | NO |
| 12 | `acg_mod_times` | int(10,0) | NO |
| 13 | `acg_mod_by` | varchar(12) | NO |
| 14 | `acg_mod_date` | datetime | NO |
| 15 | `acg_pst` | bit | NO |
| 16 | `acg_pst_by` | varchar(12) | NO |
| 17 | `acg_pst_date` | datetime | YES |
| 18 | `acg_char1` | varchar(255) | NO |
| 19 | `acg_char2` | varchar(255) | NO |
| 20 | `acg_char3` | varchar(255) | NO |
| 21 | `acg_char4` | varchar(255) | NO |
| 22 | `acg_char5` | varchar(255) | NO |
| 23 | `acg_char6` | varchar(255) | NO |
| 24 | `acg_qty1` | decimal(19,8) | NO |
| 25 | `acg_qty2` | decimal(19,8) | NO |

### `dbo.acgd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acgd_nbr` | varchar(15) | NO |
| 2 | `acgd_line` | int(10,0) | NO |
| 3 | `acgd_part` | varchar(30) | NO |
| 4 | `acgd_ovr_mth` | int(10,0) | NO |
| 5 | `acgd_amt_fare` | decimal(19,8) | NO |
| 6 | `acgd_amt_svc` | decimal(19,8) | NO |
| 7 | `acgd_amt_mtl` | decimal(19,8) | NO |
| 8 | `acgd_amt_others` | decimal(19,8) | NO |
| 9 | `acgd_amt_desc` | varchar(255) | NO |
| 10 | `acgd_rmks` | varchar(255) | NO |
| 11 | `acgd_crt_by` | varchar(12) | NO |
| 12 | `acgd_crt_date` | datetime | NO |
| 13 | `acgd_mod_times` | int(10,0) | NO |
| 14 | `acgd_mod_by` | varchar(12) | NO |
| 15 | `acgd_mod_date` | datetime | NO |
| 16 | `acgd_char1` | varchar(255) | NO |
| 17 | `acgd_char2` | varchar(255) | NO |
| 18 | `acgd_char3` | varchar(255) | NO |
| 19 | `acgd_char4` | varchar(255) | NO |
| 20 | `acgd_char5` | varchar(255) | NO |
| 21 | `acgd_char6` | varchar(255) | NO |
| 22 | `acgd_qty1` | decimal(19,8) | NO |
| 23 | `acgd_qty2` | decimal(19,8) | NO |
| 24 | `acgd_src_nbr` | varchar(15) | NO |
| 25 | `acgd_src_line` | int(10,0) | NO |

### `dbo.acgd2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acgd2_nbr` | varchar(15) | NO |
| 2 | `acgd2_line` | int(10,0) | NO |
| 3 | `acgd2_seq` | int(10,0) | NO |
| 4 | `acgd2_part` | varchar(30) | NO |
| 5 | `acgd2_qty` | numeric(19,8) | NO |
| 6 | `acgd2_price` | decimal(19,8) | NO |
| 7 | `acgd2_rmks` | varchar(255) | NO |
| 8 | `acgd2_crt_by` | varchar(12) | NO |
| 9 | `acgd2_crt_date` | datetime | NO |
| 10 | `acgd2_mod_times` | int(10,0) | NO |
| 11 | `acgd2_mod_by` | varchar(12) | NO |
| 12 | `acgd2_mod_date` | datetime | NO |
| 13 | `acgd2_char1` | varchar(255) | NO |
| 14 | `acgd2_char2` | varchar(255) | NO |
| 15 | `acgd2_char3` | varchar(255) | NO |
| 16 | `acgd2_char4` | varchar(255) | NO |
| 17 | `acgd2_char5` | varchar(255) | NO |
| 18 | `acgd2_char6` | varchar(255) | NO |
| 19 | `acgd2_qty1` | decimal(19,8) | NO |
| 20 | `acgd2_qty2` | decimal(19,8) | NO |
| 21 | `acgd2_src_nbr` | varchar(15) | NO |
| 22 | `acgd2_src_line` | int(10,0) | NO |

### `dbo.acm_bal` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acm_company` | varchar(8) | NO |
| 2 | `acm_ac_code` | varchar(15) | NO |
| 3 | `acm_year` | int(10,0) | NO |
| 4 | `acm_month` | int(10,0) | NO |
| 5 | `acm_curr` | varchar(4) | NO |
| 6 | `acm_debit_base` | numeric(19,8) | NO |
| 7 | `acm_credit_base` | numeric(19,8) | NO |
| 8 | `acm_debit_amt` | numeric(19,8) | NO |
| 9 | `acm_credit_amt` | numeric(19,8) | NO |
| 10 | `acm_debit_qty` | numeric(19,8) | NO |
| 11 | `acm_credit_qty` | numeric(19,8) | NO |
| 12 | `acm_udebit_base` | numeric(19,8) | NO |
| 13 | `acm_ucredit_base` | numeric(19,8) | NO |
| 14 | `acm_udebit_amt` | numeric(19,8) | NO |
| 15 | `acm_ucredit_amt` | numeric(19,8) | NO |
| 16 | `acm_udebit_qty` | numeric(19,8) | NO |
| 17 | `acm_ucredit_qty` | numeric(19,8) | NO |

### `dbo.acm1_bal` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acm1_company` | varchar(8) | NO |
| 2 | `acm1_dept` | varchar(10) | NO |
| 3 | `acm1_ac_code` | varchar(15) | NO |
| 4 | `acm1_year` | int(10,0) | NO |
| 5 | `acm1_month` | int(10,0) | NO |
| 6 | `acm1_curr` | varchar(4) | NO |
| 7 | `acm1_debit_base` | numeric(19,8) | NO |
| 8 | `acm1_credit_base` | numeric(19,8) | NO |
| 9 | `acm1_debit_amt` | numeric(19,8) | NO |
| 10 | `acm1_credit_amt` | numeric(19,8) | NO |
| 11 | `acm1_debit_qty` | numeric(19,8) | NO |
| 12 | `acm1_credit_qty` | numeric(19,8) | NO |
| 13 | `acm1_udebit_base` | numeric(19,8) | NO |
| 14 | `acm1_ucredit_base` | numeric(19,8) | NO |
| 15 | `acm1_udebit_amt` | numeric(19,8) | NO |
| 16 | `acm1_ucredit_amt` | numeric(19,8) | NO |
| 17 | `acm1_udebit_qty` | numeric(19,8) | NO |
| 18 | `acm1_ucredit_qty` | numeric(19,8) | NO |

### `dbo.acm2_bal` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acm2_company` | varchar(8) | NO |
| 2 | `acm2_ac_code` | varchar(15) | NO |
| 3 | `acm2_seq` | varchar(1) | NO |
| 4 | `acm2_analy_item` | varchar(30) | NO |
| 5 | `acm2_year` | int(10,0) | NO |
| 6 | `acm2_month` | int(10,0) | NO |
| 7 | `acm2_curr` | varchar(4) | NO |
| 8 | `acm2_debit_base` | numeric(19,8) | NO |
| 9 | `acm2_credit_base` | numeric(19,8) | NO |
| 10 | `acm2_debit_amt` | numeric(19,8) | NO |
| 11 | `acm2_credit_amt` | numeric(19,8) | NO |
| 12 | `acm2_debit_qty` | numeric(19,8) | NO |
| 13 | `acm2_credit_qty` | numeric(19,8) | NO |
| 14 | `acm2_udebit_base` | numeric(19,8) | NO |
| 15 | `acm2_ucredit_base` | numeric(19,8) | NO |
| 16 | `acm2_udebit_amt` | numeric(19,8) | NO |
| 17 | `acm2_ucredit_amt` | numeric(19,8) | NO |
| 18 | `acm2_udebit_qty` | numeric(19,8) | NO |
| 19 | `acm2_ucredit_qty` | numeric(19,8) | NO |

### `dbo.adj_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `adj_adj` | varchar(15) | NO |
| 2 | `adj_date` | datetime | NO |
| 3 | `adj_checker` | varchar(12) | NO |
| 4 | `adj_loc` | varchar(8) | NO |
| 5 | `adj_type` | varchar(1) | NO |
| 6 | `adj_rmks` | varchar(255) | NO |
| 7 | `adj_site` | varchar(8) | NO |
| 8 | `adj_wf_status` | varchar(1) | NO |
| 9 | `adj_prog_code` | varchar(12) | NO |
| 10 | `adj_doc_code` | varchar(12) | NO |
| 11 | `adj_crt_by` | varchar(12) | NO |
| 12 | `adj_crt_date` | datetime | NO |
| 13 | `adj_mod_times` | int(10,0) | NO |
| 14 | `adj_mod_by` | varchar(12) | NO |
| 15 | `adj_mod_date` | datetime | NO |
| 16 | `adj_pst` | bit | NO |
| 17 | `adj_pst_by` | varchar(12) | NO |
| 18 | `adj_pst_date` | datetime | YES |
| 19 | `adj_char1` | varchar(255) | NO |
| 20 | `adj_char2` | varchar(255) | NO |
| 21 | `adj_char3` | varchar(255) | NO |
| 22 | `adj_char4` | varchar(255) | NO |
| 23 | `adj_char5` | varchar(255) | NO |
| 24 | `adj_char6` | varchar(255) | NO |
| 25 | `adj_qty1` | decimal(19,8) | NO |
| 26 | `adj_qty2` | decimal(19,8) | NO |
| 27 | `adj_data_src` | varchar(1) | NO |
| 28 | `adj_data_id` | varchar(255) | NO |
| 29 | `adj_chk` | bit | NO |
| 30 | `adj_chk_by` | varchar(12) | NO |
| 31 | `adj_chk_date` | datetime | YES |

### `dbo.adjd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `adjd_adj` | varchar(15) | NO |
| 2 | `adjd_line` | int(10,0) | NO |
| 3 | `adjd_part` | varchar(30) | NO |
| 4 | `adjd_loc` | varchar(8) | NO |
| 5 | `adjd_lot` | varchar(18) | NO |
| 6 | `adjd_qty_rec` | numeric(19,8) | NO |
| 7 | `adjd_qty_cnt` | numeric(19,8) | NO |
| 8 | `adjd_qty_diff` | numeric(19,8) | NO |
| 9 | `adjd_reason` | varchar(30) | NO |
| 10 | `adjd_rmks` | varchar(255) | NO |
| 11 | `adjd_crt_by` | varchar(12) | NO |
| 12 | `adjd_crt_date` | datetime | NO |
| 13 | `adjd_mod_times` | int(10,0) | NO |
| 14 | `adjd_mod_by` | varchar(12) | NO |
| 15 | `adjd_mod_date` | datetime | NO |
| 16 | `adjd_char1` | varchar(255) | NO |
| 17 | `adjd_char2` | varchar(255) | NO |
| 18 | `adjd_char3` | varchar(255) | NO |
| 19 | `adjd_char4` | varchar(255) | NO |
| 20 | `adjd_char5` | varchar(255) | NO |
| 21 | `adjd_char6` | varchar(255) | NO |
| 22 | `adjd_qty1` | decimal(19,8) | NO |
| 23 | `adjd_qty2` | decimal(19,8) | NO |
| 24 | `adjd_data_src` | varchar(1) | NO |
| 25 | `adjd_data_id` | varchar(255) | NO |

### `dbo.adjsd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `adjsd_adj` | varchar(15) | NO |
| 2 | `adjsd_line` | int(10,0) | NO |
| 3 | `adjsd_part` | varchar(30) | NO |
| 4 | `adjsd_loc` | varchar(8) | NO |
| 5 | `adjsd_pos` | varchar(30) | NO |
| 6 | `adjsd_qty_rec` | numeric(19,8) | NO |
| 7 | `adjsd_qty_cnt` | numeric(19,8) | NO |
| 8 | `adjsd_rmks` | varchar(255) | NO |
| 9 | `adjsd_crt_by` | varchar(12) | NO |
| 10 | `adjsd_crt_date` | datetime | NO |
| 11 | `adjsd_mod_times` | int(10,0) | NO |
| 12 | `adjsd_mod_by` | varchar(12) | NO |
| 13 | `adjsd_mod_date` | datetime | NO |
| 14 | `adjsd_data_src` | varchar(1) | NO |
| 15 | `adjsd_data_id` | varchar(255) | NO |
| 16 | `adjsd_char1` | varchar(255) | NO |
| 17 | `adjsd_char2` | varchar(255) | NO |
| 18 | `adjsd_char3` | varchar(255) | NO |
| 19 | `adjsd_char4` | varchar(255) | NO |
| 20 | `adjsd_char5` | varchar(255) | NO |
| 21 | `adjsd_char6` | varchar(255) | NO |
| 22 | `adjsd_qty1` | decimal(19,8) | NO |
| 23 | `adjsd_qty2` | decimal(19,8) | NO |

### `dbo.adjsd2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `adjsd2_adj` | varchar(15) | NO |
| 2 | `adjsd2_line` | int(10,0) | NO |
| 3 | `adjsd2_seq` | int(10,0) | NO |
| 4 | `adjsd2_part` | varchar(30) | NO |
| 5 | `adjsd2_loc` | varchar(8) | NO |
| 6 | `adjsd2_pos` | varchar(30) | NO |
| 7 | `adjsd2_lot` | varchar(18) | NO |
| 8 | `adjsd2_qty_rec` | numeric(19,8) | NO |
| 9 | `adjsd2_qty_cnt` | numeric(19,8) | NO |
| 10 | `adjsd2_barcode` | varchar(1000) | NO |
| 11 | `adjsd2_rmks` | varchar(255) | NO |
| 12 | `adjsd2_crt_by` | varchar(12) | NO |
| 13 | `adjsd2_crt_date` | datetime | NO |
| 14 | `adjsd2_mod_times` | int(10,0) | NO |
| 15 | `adjsd2_mod_by` | varchar(12) | NO |
| 16 | `adjsd2_mod_date` | datetime | NO |
| 17 | `adjsd2_data_src` | varchar(1) | NO |
| 18 | `adjsd2_data_id` | varchar(255) | NO |
| 19 | `adjsd2_char1` | varchar(255) | NO |
| 20 | `adjsd2_char2` | varchar(255) | NO |
| 21 | `adjsd2_char3` | varchar(255) | NO |
| 22 | `adjsd2_char4` | varchar(255) | NO |
| 23 | `adjsd2_char5` | varchar(255) | NO |
| 24 | `adjsd2_char6` | varchar(255) | NO |
| 25 | `adjsd2_qty1` | decimal(19,8) | NO |
| 26 | `adjsd2_qty2` | decimal(19,8) | NO |

### `dbo.ap_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ap_nbr` | varchar(15) | NO |
| 2 | `ap_date` | datetime | NO |
| 3 | `ap_doc_code` | varchar(15) | NO |
| 4 | `ap_vendor` | varchar(8) | NO |
| 5 | `ap_company` | varchar(8) | NO |
| 6 | `ap_vo_nbr` | varchar(15) | NO |
| 7 | `ap_curr` | varchar(4) | NO |
| 8 | `ap_exch_rate` | decimal(19,8) | NO |
| 9 | `ap_terms` | varchar(10) | NO |
| 10 | `ap_due_date` | datetime | YES |
| 11 | `ap_disc_date` | datetime | YES |
| 12 | `ap_disc_pct` | decimal(19,8) | NO |
| 13 | `ap_inv_type` | varchar(1) | NO |
| 14 | `ap_vat_method` | varchar(1) | NO |
| 15 | `ap_vat_rate` | numeric(19,8) | NO |
| 16 | `ap_inv_nbr` | varchar(255) | NO |
| 17 | `ap_inv_date` | datetime | YES |
| 18 | `ap_inv_amta` | numeric(19,8) | NO |
| 19 | `ap_inv_amtb` | numeric(19,8) | NO |
| 20 | `ap_inv_amt` | numeric(19,8) | NO |
| 21 | `ap_last_exch_rate` | decimal(19,8) | NO |
| 22 | `ap_tot_exch_amt` | numeric(19,8) | NO |
| 23 | `ap_amt` | numeric(19,8) | NO |
| 24 | `ap_curr_amt` | numeric(19,8) | NO |
| 25 | `ap_curr_vat` | numeric(19,8) | NO |
| 26 | `ap_paid_amt` | numeric(19,8) | NO |
| 27 | `ap_base_ap_amt` | numeric(19,8) | NO |
| 28 | `ap_base_amt` | numeric(19,8) | NO |
| 29 | `ap_base_vat_amt` | numeric(19,8) | NO |
| 30 | `ap_rmks` | varchar(255) | NO |
| 31 | `ap_closed` | bit | NO |
| 32 | `ap_hold` | bit | NO |
| 33 | `ap_prt_cnt` | int(10,0) | NO |
| 34 | `ap_prog_code` | varchar(12) | NO |
| 35 | `ap_crt_by` | varchar(12) | NO |
| 36 | `ap_crt_date` | datetime | NO |
| 37 | `ap_mod_times` | int(10,0) | NO |
| 38 | `ap_mod_by` | varchar(12) | NO |
| 39 | `ap_mod_date` | datetime | NO |
| 40 | `ap_pst` | bit | NO |
| 41 | `ap_pst_by` | varchar(12) | NO |
| 42 | `ap_pst_date` | datetime | YES |
| 43 | `ap_char1` | varchar(255) | NO |
| 44 | `ap_char2` | varchar(255) | NO |
| 45 | `ap_char3` | varchar(255) | NO |
| 46 | `ap_char4` | varchar(255) | NO |
| 47 | `ap_char5` | varchar(255) | NO |
| 48 | `ap_char6` | varchar(255) | NO |
| 49 | `ap_qty1` | decimal(19,8) | NO |
| 50 | `ap_qty2` | decimal(19,8) | NO |

### `dbo.apc_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `apc_apc` | int(10,0) | NO |
| 2 | `apc_adj_amt` | numeric(19,8) | NO |
| 3 | `apc_init_date` | datetime | NO |
| 4 | `apc_iqc` | bit | NO |
| 5 | `apc_inv_pay` | bit | NO |
| 6 | `apc_inv_right` | varchar(255) | NO |
| 7 | `apc_payment_ac` | varchar(15) | NO |
| 8 | `apc_ap_ac1` | varchar(15) | NO |
| 9 | `apc_debit_diff` | varchar(15) | NO |
| 10 | `apc_credit_diff` | varchar(15) | NO |
| 11 | `apc_disc_ac` | varchar(15) | NO |
| 12 | `apc_adv_ac` | varchar(15) | NO |
| 13 | `apc_exch_ac` | varchar(15) | NO |
| 14 | `apc_inv_ac` | varchar(15) | NO |
| 15 | `apc_to_vo_date` | datetime | NO |
| 16 | `apc_ap_gl` | varchar(1) | NO |
| 17 | `apc_apn_gl` | varchar(1) | NO |
| 18 | `apc_pm_gl` | varchar(1) | NO |
| 19 | `apc_pma_gl` | varchar(1) | NO |
| 20 | `apc_ap_doc` | varchar(15) | NO |
| 21 | `apc_apn_doc` | varchar(15) | NO |
| 22 | `apc_pm_doc` | varchar(15) | NO |
| 23 | `apc_pma_doc` | varchar(15) | NO |
| 24 | `apc_ap_gl_code` | varchar(1) | NO |
| 25 | `apc_apn_gl_code` | varchar(1) | NO |
| 26 | `apc_pm_gl_code` | varchar(1) | NO |
| 27 | `apc_pma_gl_code` | varchar(1) | NO |
| 28 | `apc_crt_by` | varchar(12) | NO |
| 29 | `apc_crt_date` | datetime | NO |
| 30 | `apc_mod_times` | int(10,0) | NO |
| 31 | `apc_mod_by` | varchar(12) | NO |
| 32 | `apc_mod_date` | datetime | NO |
| 33 | `apc_char1` | varchar(255) | NO |
| 34 | `apc_char2` | varchar(255) | NO |
| 35 | `apc_char3` | varchar(255) | NO |
| 36 | `apc_char4` | varchar(255) | NO |
| 37 | `apc_char5` | varchar(255) | NO |
| 38 | `apc_char6` | varchar(255) | NO |
| 39 | `apc_qty1` | decimal(19,8) | NO |
| 40 | `apc_qty2` | decimal(19,8) | NO |
| 41 | `apc_to_vo_type` | varchar(1) | NO |
| 42 | `apc_inv_ac2` | varchar(15) | NO |
| 43 | `apc_claim_ac` | varchar(15) | NO |
| 44 | `apc_inv_ac3` | varchar(15) | NO |
| 45 | `apc_anc_gl` | varchar(1) | NO |
| 46 | `apc_anc_doc` | varchar(15) | NO |
| 47 | `apc_anc_gl_code` | varchar(1) | NO |
| 48 | `apc_zero_inv` | bit | NO |
| 49 | `apc_pma_spec_perm` | varchar(255) | NO |

### `dbo.apd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `apd_nbr` | varchar(15) | NO |
| 2 | `apd_line` | int(10,0) | NO |
| 3 | `apd_src` | varchar(1) | NO |
| 4 | `apd_src_nbr` | varchar(15) | NO |
| 5 | `apd_src_line` | int(10,0) | NO |
| 6 | `apd_src_date` | datetime | YES |
| 7 | `apd_qty_pay` | numeric(19,8) | NO |
| 8 | `apd_src_cost` | decimal(19,8) | NO |
| 9 | `apd_pur_cost` | decimal(19,8) | NO |
| 10 | `apd_minus_amt` | numeric(19,8) | NO |
| 11 | `apd_ap_amt` | numeric(19,8) | NO |
| 12 | `apd_curr_amt` | numeric(19,8) | NO |
| 13 | `apd_curr_vat` | numeric(19,8) | NO |
| 14 | `apd_base_ap_amt` | numeric(19,8) | NO |
| 15 | `apd_base_amt` | numeric(19,8) | NO |
| 16 | `apd_base_vat` | numeric(19,8) | NO |
| 17 | `apd_ac_code` | varchar(15) | NO |
| 18 | `apd_dept` | varchar(30) | NO |
| 19 | `apd_analy1_code` | varchar(30) | NO |
| 20 | `apd_analy1_name` | varchar(255) | NO |
| 21 | `apd_analy2_code` | varchar(30) | NO |
| 22 | `apd_analy2_name` | varchar(255) | NO |
| 23 | `apd_analy3_code` | varchar(30) | NO |
| 24 | `apd_analy3_name` | varchar(255) | NO |
| 25 | `apd_analy4_code` | varchar(30) | NO |
| 26 | `apd_analy4_name` | varchar(255) | NO |
| 27 | `apd_inv_amt` | numeric(19,8) | NO |
| 28 | `apd_inv_nbr` | varchar(255) | NO |
| 29 | `apd_rmks` | varchar(255) | NO |
| 30 | `apd_crt_by` | varchar(12) | NO |
| 31 | `apd_crt_date` | datetime | NO |
| 32 | `apd_mod_times` | int(10,0) | NO |
| 33 | `apd_mod_by` | varchar(12) | NO |
| 34 | `apd_mod_date` | datetime | NO |
| 35 | `apd_char1` | varchar(255) | NO |
| 36 | `apd_char2` | varchar(255) | NO |
| 37 | `apd_char3` | varchar(255) | NO |
| 38 | `apd_char4` | varchar(255) | NO |
| 39 | `apd_char5` | varchar(255) | NO |
| 40 | `apd_char6` | varchar(255) | NO |
| 41 | `apd_qty1` | decimal(19,8) | NO |
| 42 | `apd_qty2` | decimal(19,8) | NO |

### `dbo.apn_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `apn_nbr` | varchar(15) | NO |
| 2 | `apn_doc_code` | varchar(15) | NO |
| 3 | `apn_company` | varchar(8) | NO |
| 4 | `apn_date` | datetime | NO |
| 5 | `apn_vendor` | varchar(8) | NO |
| 6 | `apn_curr` | varchar(4) | NO |
| 7 | `apn_vat_rate` | numeric(19,8) | NO |
| 8 | `apn_inv_type` | varchar(1) | NO |
| 9 | `apn_inv_nbr` | varchar(255) | NO |
| 10 | `apn_vo_nbr` | varchar(15) | NO |
| 11 | `apn_rmks` | varchar(255) | NO |
| 12 | `apn_crt_by` | varchar(12) | NO |
| 13 | `apn_crt_date` | datetime | NO |
| 14 | `apn_mod_times` | int(10,0) | NO |
| 15 | `apn_mod_by` | varchar(12) | NO |
| 16 | `apn_mod_date` | datetime | NO |
| 17 | `apn_pst` | bit | NO |
| 18 | `apn_pst_by` | varchar(12) | NO |
| 19 | `apn_pst_date` | datetime | YES |
| 20 | `apn_prog_code` | varchar(12) | NO |
| 21 | `apn_char1` | varchar(255) | NO |
| 22 | `apn_char2` | varchar(255) | NO |
| 23 | `apn_char3` | varchar(255) | NO |
| 24 | `apn_char4` | varchar(255) | NO |
| 25 | `apn_char5` | varchar(255) | NO |
| 26 | `apn_char6` | varchar(255) | NO |
| 27 | `apn_qty1` | decimal(19,8) | NO |
| 28 | `apn_qty2` | decimal(19,8) | NO |
| 29 | `apn_amt_tot` | numeric(19,8) | NO |
| 30 | `apn_amt_ex` | numeric(19,8) | NO |
| 31 | `apn_amt_tax` | numeric(19,8) | NO |
| 32 | `apn_cert_amt` | numeric(19,8) | YES |
| 33 | `apn_cert_vat` | numeric(19,8) | YES |

### `dbo.apnd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `apnd_nbr` | varchar(15) | NO |
| 2 | `apnd_line` | int(10,0) | NO |
| 3 | `apnd_apd_nbr` | varchar(15) | NO |
| 4 | `apnd_apd_line` | int(10,0) | NO |
| 5 | `apnd_inv_amt` | numeric(19,8) | NO |
| 6 | `apnd_rmks` | varchar(255) | NO |
| 7 | `apnd_crt_by` | varchar(12) | NO |
| 8 | `apnd_crt_date` | datetime | NO |
| 9 | `apnd_mod_times` | int(10,0) | NO |
| 10 | `apnd_mod_by` | varchar(12) | NO |
| 11 | `apnd_mod_date` | datetime | NO |
| 12 | `apnd_char1` | varchar(255) | NO |
| 13 | `apnd_char2` | varchar(255) | NO |
| 14 | `apnd_char3` | varchar(255) | NO |
| 15 | `apnd_char4` | varchar(255) | NO |
| 16 | `apnd_char5` | varchar(255) | NO |
| 17 | `apnd_char6` | varchar(255) | NO |
| 18 | `apnd_qty1` | decimal(19,8) | NO |
| 19 | `apnd_qty2` | decimal(19,8) | NO |
| 20 | `apnd_amt_ex` | numeric(19,8) | NO |
| 21 | `apnd_amt_tax` | numeric(19,8) | NO |

### `dbo.ar_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ar_nbr` | varchar(15) | NO |
| 2 | `ar_date` | datetime | NO |
| 3 | `ar_doc_code` | varchar(15) | NO |
| 4 | `ar_customer` | varchar(8) | NO |
| 5 | `ar_company` | varchar(8) | NO |
| 6 | `ar_vo_nbr` | varchar(15) | NO |
| 7 | `ar_curr` | varchar(4) | NO |
| 8 | `ar_exch_rate` | decimal(19,8) | NO |
| 9 | `ar_terms` | varchar(10) | NO |
| 10 | `ar_due_date` | datetime | YES |
| 11 | `ar_disc_date` | datetime | YES |
| 12 | `ar_disc_pct` | decimal(19,8) | NO |
| 13 | `ar_inv_type` | varchar(1) | NO |
| 14 | `ar_vat_method` | varchar(1) | NO |
| 15 | `ar_vat_rate` | numeric(19,8) | NO |
| 16 | `ar_inv_nbr` | varchar(255) | NO |
| 17 | `ar_inv_date` | datetime | YES |
| 18 | `ar_inv_amta` | numeric(19,8) | NO |
| 19 | `ar_inv_amtb` | numeric(19,8) | NO |
| 20 | `ar_inv_amt` | numeric(19,8) | NO |
| 21 | `ar_last_exch_rate` | decimal(19,8) | NO |
| 22 | `ar_tot_exch_amt` | numeric(19,8) | NO |
| 23 | `ar_amt` | numeric(19,8) | NO |
| 24 | `ar_curr_amt` | numeric(19,8) | NO |
| 25 | `ar_curr_vat` | numeric(19,8) | NO |
| 26 | `ar_paid_amt` | numeric(19,8) | NO |
| 27 | `ar_base_ar_amt` | numeric(19,8) | NO |
| 28 | `ar_base_amt` | numeric(19,8) | NO |
| 29 | `ar_base_vat_amt` | numeric(19,8) | NO |
| 30 | `ar_rmks` | varchar(255) | NO |
| 31 | `ar_closed` | bit | NO |
| 32 | `ar_hold` | bit | NO |
| 33 | `ar_prt_cnt` | int(10,0) | NO |
| 34 | `ar_prog_code` | varchar(12) | NO |
| 35 | `ar_crt_by` | varchar(12) | NO |
| 36 | `ar_crt_date` | datetime | NO |
| 37 | `ar_mod_times` | int(10,0) | NO |
| 38 | `ar_mod_by` | varchar(12) | NO |
| 39 | `ar_mod_date` | datetime | NO |
| 40 | `ar_pst` | bit | NO |
| 41 | `ar_pst_by` | varchar(12) | NO |
| 42 | `ar_pst_date` | datetime | YES |
| 43 | `ar_char1` | varchar(255) | NO |
| 44 | `ar_char2` | varchar(255) | NO |
| 45 | `ar_char3` | varchar(255) | NO |
| 46 | `ar_char4` | varchar(255) | NO |
| 47 | `ar_char5` | varchar(255) | NO |
| 48 | `ar_char6` | varchar(255) | NO |
| 49 | `ar_qty1` | decimal(19,8) | NO |
| 50 | `ar_qty2` | decimal(19,8) | NO |

### `dbo.arc_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `arc_arc` | int(10,0) | NO |
| 2 | `arc_adj_amt` | numeric(19,8) | NO |
| 3 | `arc_init_date` | datetime | NO |
| 4 | `arc_inv_right` | varchar(80) | NO |
| 5 | `arc_rcv_ac` | varchar(15) | NO |
| 6 | `arc_ar_ac1` | varchar(15) | NO |
| 7 | `arc_debit_diff` | varchar(15) | NO |
| 8 | `arc_credit_diff` | varchar(15) | NO |
| 9 | `arc_disc_ac` | varchar(15) | NO |
| 10 | `arc_exch_ac` | varchar(15) | NO |
| 11 | `arc_vat_ac` | varchar(15) | NO |
| 12 | `arc_to_vo_date` | datetime | NO |
| 13 | `arc_ar_gl` | varchar(1) | NO |
| 14 | `arc_cpm_gl` | varchar(1) | NO |
| 15 | `arc_cpma_gl` | varchar(1) | NO |
| 16 | `arc_ar_doc` | varchar(15) | NO |
| 17 | `arc_cpm_doc` | varchar(15) | NO |
| 18 | `arc_cpma_doc` | varchar(15) | NO |
| 19 | `arc_ar_gl_code` | varchar(1) | NO |
| 20 | `arc_cpm_gl_code` | varchar(1) | NO |
| 21 | `arc_cpma_gl_code` | varchar(1) | NO |
| 22 | `arc_crt_by` | varchar(12) | NO |
| 23 | `arc_crt_date` | datetime | NO |
| 24 | `arc_mod_times` | int(10,0) | NO |
| 25 | `arc_mod_by` | varchar(12) | NO |
| 26 | `arc_mod_date` | datetime | NO |
| 27 | `arc_char1` | varchar(255) | NO |
| 28 | `arc_char2` | varchar(255) | NO |
| 29 | `arc_char3` | varchar(255) | NO |
| 30 | `arc_char4` | varchar(255) | NO |
| 31 | `arc_char5` | varchar(255) | NO |
| 32 | `arc_char6` | varchar(255) | NO |
| 33 | `arc_qty1` | decimal(19,8) | NO |
| 34 | `arc_qty2` | decimal(19,8) | NO |
| 35 | `arc_to_vo_type` | varchar(1) | NO |
| 36 | `arc_vat_ac2` | varchar(15) | NO |
| 37 | `arc_inv_gl` | varchar(1) | NO |
| 38 | `arc_inv_doc` | varchar(15) | NO |
| 39 | `arc_inv_gl_code` | varchar(1) | NO |

### `dbo.ard_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ard_nbr` | varchar(15) | NO |
| 2 | `ard_line` | int(10,0) | NO |
| 3 | `ard_src` | varchar(1) | NO |
| 4 | `ard_src_nbr` | varchar(15) | NO |
| 5 | `ard_src_line` | int(10,0) | NO |
| 6 | `ard_src_date` | datetime | YES |
| 7 | `ard_qty_pay` | numeric(19,8) | NO |
| 8 | `ard_src_price` | decimal(19,8) | NO |
| 9 | `ard_sod_price` | decimal(19,8) | NO |
| 10 | `ard_minus_amt` | numeric(19,8) | NO |
| 11 | `ard_ar_amt` | numeric(19,8) | NO |
| 12 | `ard_curr_amt` | numeric(19,8) | NO |
| 13 | `ard_curr_vat` | numeric(19,8) | NO |
| 14 | `ard_base_ar_amt` | numeric(19,8) | NO |
| 15 | `ard_base_amt` | numeric(19,8) | NO |
| 16 | `ard_base_vat` | numeric(19,8) | NO |
| 17 | `ard_ac_code` | varchar(15) | NO |
| 18 | `ard_dept` | varchar(30) | NO |
| 19 | `ard_analy1_code` | varchar(30) | NO |
| 20 | `ard_analy1_name` | varchar(255) | NO |
| 21 | `ard_analy2_code` | varchar(30) | NO |
| 22 | `ard_analy2_name` | varchar(255) | NO |
| 23 | `ard_analy3_code` | varchar(30) | NO |
| 24 | `ard_analy3_name` | varchar(255) | NO |
| 25 | `ard_analy4_code` | varchar(30) | NO |
| 26 | `ard_analy4_name` | varchar(255) | NO |
| 27 | `ard_rmks` | varchar(255) | NO |
| 28 | `ard_crt_by` | varchar(12) | NO |
| 29 | `ard_crt_date` | datetime | NO |
| 30 | `ard_mod_times` | int(10,0) | NO |
| 31 | `ard_mod_by` | varchar(12) | NO |
| 32 | `ard_mod_date` | datetime | NO |
| 33 | `ard_char1` | varchar(255) | NO |
| 34 | `ard_char2` | varchar(255) | NO |
| 35 | `ard_char3` | varchar(255) | NO |
| 36 | `ard_char4` | varchar(255) | NO |
| 37 | `ard_char5` | varchar(255) | NO |
| 38 | `ard_char6` | varchar(255) | NO |
| 39 | `ard_qty1` | decimal(19,8) | NO |
| 40 | `ard_qty2` | decimal(19,8) | NO |
| 41 | `ard_inv_nbr` | varchar(15) | NO |
| 42 | `ard_inv_line` | int(10,0) | NO |

### `dbo.ard_export` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ar_user` | varchar(12) | NO |
| 2 | `ard_nbr` | varchar(15) | NO |
| 3 | `ard_line` | int(10,0) | NO |
| 4 | `ar_date` | datetime | YES |
| 5 | `ar_customer` | varchar(8) | NO |
| 6 | `ar_vat_rate` | numeric(19,8) | NO |
| 7 | `ar_curr` | varchar(4) | NO |
| 8 | `ar_terms` | varchar(10) | NO |
| 9 | `ar_amt` | numeric(19,8) | NO |
| 10 | `ar_paid_amt` | numeric(19,8) | NO |
| 11 | `ar_exch_rate` | numeric(19,8) | NO |
| 12 | `ar_doc_code` | varchar(15) | NO |
| 13 | `ard_src` | varchar(1) | NO |
| 14 | `ard_src_nbr` | varchar(15) | NO |
| 15 | `ard_src_line` | int(10,0) | NO |
| 16 | `ard_src_date` | datetime | YES |
| 17 | `ard_qty_pay` | numeric(19,8) | NO |
| 18 | `ard_sod_price` | numeric(19,8) | NO |
| 19 | `ard_minus_amt` | numeric(19,8) | NO |
| 20 | `ard_ar_amt` | numeric(19,8) | NO |
| 21 | `ard_base_ar_amt` | numeric(19,8) | NO |
| 22 | `ard_rmks` | varchar(255) | NO |
| 23 | `cm_sort` | varchar(255) | NO |
| 24 | `cm_slspsn` | varchar(12) | NO |
| 25 | `slspsn_name` | varchar(50) | NO |
| 26 | `ct_desc` | varchar(255) | NO |
| 27 | `src_name` | varchar(255) | NO |
| 28 | `sdh_so_nbr` | varchar(15) | NO |
| 29 | `sdh_sod_line` | int(10,0) | NO |
| 30 | `sdh_part` | varchar(30) | NO |
| 31 | `sdh_um` | varchar(4) | NO |
| 32 | `pt_desc1` | varchar(255) | NO |
| 33 | `pt_spec` | varchar(255) | NO |
| 34 | `so_po` | varchar(255) | NO |
| 35 | `ard_paid_amt` | numeric(19,8) | NO |
| 36 | `ard_paid_base` | numeric(19,8) | NO |
| 37 | `ard_status` | bit | NO |
| 38 | `ard_curr_amt` | numeric(19,8) | NO |
| 39 | `ard_base_amt` | numeric(19,8) | NO |
| 40 | `ard_curr_vat` | numeric(19,8) | NO |
| 41 | `ard_base_vat` | numeric(19,8) | NO |
| 42 | `unpaid_amt` | numeric(19,8) | NO |
| 43 | `unpaid_base_amt` | numeric(19,8) | NO |
| 44 | `unpaid_amt_unvat` | numeric(19,8) | NO |
| 45 | `unpaid_amt_vat` | numeric(19,8) | NO |
| 46 | `unpaid_base_unvat` | numeric(19,8) | NO |
| 47 | `unpaid_base_vat` | numeric(19,8) | NO |
| 48 | `sod_cust_part` | varchar(30) | NO |
| 49 | `sod_cust_desc` | varchar(255) | NO |
| 50 | `cm_headq` | varchar(8) | NO |
| 51 | `headq_sort` | varchar(255) | NO |
| 52 | `so_buyer` | varchar(255) | NO |
| 53 | `so_rd_group` | varchar(12) | NO |
| 54 | `rd_group_name` | varchar(50) | NO |
| 55 | `dn_txt` | varchar(8) | NO |
| 56 | `dn_txt_desc` | varchar(255) | NO |

### `dbo.asdt_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asdt_code` | varchar(30) | NO |
| 2 | `asdt_desc` | varchar(255) | NO |
| 3 | `asdt_rmks` | varchar(255) | NO |
| 4 | `asdt_start` | datetime | NO |
| 5 | `asdt_end` | datetime | NO |
| 6 | `asdt_rtn_need` | varchar(1) | NO |
| 7 | `asdt_rtn_seq` | varchar(1) | NO |
| 8 | `asdt_iqc_need` | varchar(1) | NO |
| 9 | `asdt_other_pt` | varchar(1) | NO |
| 10 | `asdt_qty_more` | varchar(1) | NO |
| 11 | `asdt_fee_ctrl` | varchar(1) | NO |
| 12 | `asdt_crt_by` | varchar(12) | NO |
| 13 | `asdt_crt_date` | datetime | NO |
| 14 | `asdt_mod_times` | int(10,0) | NO |
| 15 | `asdt_mod_by` | varchar(12) | NO |
| 16 | `asdt_mod_date` | datetime | NO |
| 17 | `asdt_pst` | bit | NO |
| 18 | `asdt_pst_by` | varchar(12) | NO |
| 19 | `asdt_pst_date` | datetime | YES |
| 20 | `asdt_char1` | varchar(255) | NO |
| 21 | `asdt_char2` | varchar(255) | NO |
| 22 | `asdt_char3` | varchar(255) | NO |
| 23 | `asdt_char4` | varchar(255) | NO |
| 24 | `asdt_char5` | varchar(255) | NO |
| 25 | `asdt_char6` | varchar(255) | NO |
| 26 | `asdt_qty1` | decimal(19,8) | NO |
| 27 | `asdt_qty2` | decimal(19,8) | NO |

### `dbo.asi_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asi_nbr` | varchar(15) | NO |
| 2 | `asi_date` | datetime | NO |
| 3 | `asi_type` | varchar(1) | NO |
| 4 | `asi_cust` | varchar(8) | NO |
| 5 | `asi_act_date` | datetime | NO |
| 6 | `asi_rmks` | varchar(255) | NO |
| 7 | `asi_site` | varchar(8) | NO |
| 8 | `asi_wf_status` | varchar(1) | NO |
| 9 | `asi_prog_code` | varchar(12) | NO |
| 10 | `asi_crt_by` | varchar(12) | NO |
| 11 | `asi_crt_date` | datetime | NO |
| 12 | `asi_mod_times` | int(10,0) | NO |
| 13 | `asi_mod_by` | varchar(12) | NO |
| 14 | `asi_mod_date` | datetime | NO |
| 15 | `asi_pst` | bit | NO |
| 16 | `asi_pst_by` | varchar(12) | NO |
| 17 | `asi_pst_date` | datetime | YES |
| 18 | `asi_char1` | varchar(255) | NO |
| 19 | `asi_char2` | varchar(255) | NO |
| 20 | `asi_char3` | varchar(255) | NO |
| 21 | `asi_char4` | varchar(255) | NO |
| 22 | `asi_char5` | varchar(255) | NO |
| 23 | `asi_char6` | varchar(255) | NO |
| 24 | `asi_qty1` | decimal(19,8) | NO |
| 25 | `asi_qty2` | decimal(19,8) | NO |

### `dbo.asid_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asid_nbr` | varchar(15) | NO |
| 2 | `asid_line` | int(10,0) | NO |
| 3 | `asid_part` | varchar(30) | NO |
| 4 | `asid_qty_a` | numeric(19,8) | NO |
| 5 | `asid_qty_b` | numeric(19,8) | NO |
| 6 | `asid_qty_c` | numeric(19,8) | NO |
| 7 | `asid_req` | varchar(30) | NO |
| 8 | `asid_src_nbr` | varchar(15) | NO |
| 9 | `asid_src_line` | int(10,0) | NO |
| 10 | `asid_ast_code` | varchar(15) | NO |
| 11 | `asid_src_date` | datetime | NO |
| 12 | `asid_replace` | bit | NO |
| 13 | `asid_rmks` | varchar(255) | NO |
| 14 | `asid_crt_by` | varchar(12) | NO |
| 15 | `asid_crt_date` | datetime | NO |
| 16 | `asid_mod_times` | int(10,0) | NO |
| 17 | `asid_mod_by` | varchar(12) | NO |
| 18 | `asid_mod_date` | datetime | NO |
| 19 | `asid_char1` | varchar(255) | NO |
| 20 | `asid_char2` | varchar(255) | NO |
| 21 | `asid_char3` | varchar(255) | NO |
| 22 | `asid_char4` | varchar(255) | NO |
| 23 | `asid_char5` | varchar(255) | NO |
| 24 | `asid_char6` | varchar(255) | NO |
| 25 | `asid_qty1` | decimal(19,8) | NO |
| 26 | `asid_qty2` | decimal(19,8) | NO |
| 27 | `asid_pro_desc` | varchar(255) | NO |
| 28 | `asid_deal_way` | varchar(30) | NO |
| 29 | `asid_fee_way` | varchar(30) | NO |
| 30 | `asid_iqc_need` | varchar(1) | NO |

### `dbo.asid3_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asid3_nbr` | varchar(15) | NO |
| 2 | `asid3_line` | int(10,0) | NO |
| 3 | `asid3_seq` | int(10,0) | NO |
| 4 | `asid3_src` | varchar(1) | NO |
| 5 | `asid3_part` | varchar(30) | NO |
| 6 | `asid3_qty` | numeric(19,8) | NO |
| 7 | `asid3_status` | varchar(1) | NO |
| 8 | `asid3_qty_out` | numeric(19,8) | NO |
| 9 | `asid3_qty_scr` | numeric(19,8) | NO |
| 10 | `asid3_rmks` | varchar(255) | NO |
| 11 | `asid3_crt_by` | varchar(12) | NO |
| 12 | `asid3_crt_date` | datetime | NO |
| 13 | `asid3_mod_times` | int(10,0) | NO |
| 14 | `asid3_mod_by` | varchar(12) | NO |
| 15 | `asid3_mod_date` | datetime | NO |
| 16 | `asid3_char1` | varchar(255) | NO |
| 17 | `asid3_char2` | varchar(255) | NO |
| 18 | `asid3_char3` | varchar(255) | NO |
| 19 | `asid3_char4` | varchar(255) | NO |
| 20 | `asid3_char5` | varchar(255) | NO |
| 21 | `asid3_char6` | varchar(255) | NO |
| 22 | `asid3_qty1` | decimal(19,8) | NO |
| 23 | `asid3_qty2` | decimal(19,8) | NO |

### `dbo.aso_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `aso_nbr` | varchar(15) | NO |
| 2 | `aso_date` | datetime | NO |
| 3 | `aso_cust` | varchar(8) | NO |
| 4 | `aso_loc` | varchar(8) | NO |
| 5 | `aso_rmks` | varchar(255) | NO |
| 6 | `aso_site` | varchar(8) | NO |
| 7 | `aso_wf_status` | varchar(1) | NO |
| 8 | `aso_prog_code` | varchar(12) | NO |
| 9 | `aso_crt_by` | varchar(12) | NO |
| 10 | `aso_crt_date` | datetime | NO |
| 11 | `aso_mod_times` | int(10,0) | NO |
| 12 | `aso_mod_by` | varchar(12) | NO |
| 13 | `aso_mod_date` | datetime | NO |
| 14 | `aso_pst` | bit | NO |
| 15 | `aso_pst_by` | varchar(12) | NO |
| 16 | `aso_pst_date` | datetime | YES |
| 17 | `aso_char1` | varchar(255) | NO |
| 18 | `aso_char2` | varchar(255) | NO |
| 19 | `aso_char3` | varchar(255) | NO |
| 20 | `aso_char4` | varchar(255) | NO |
| 21 | `aso_char5` | varchar(255) | NO |
| 22 | `aso_char6` | varchar(255) | NO |
| 23 | `aso_qty1` | decimal(19,8) | NO |
| 24 | `aso_qty2` | decimal(19,8) | NO |
| 25 | `aso_acg_nbr` | varchar(15) | NO |

### `dbo.asod_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asod_nbr` | varchar(15) | NO |
| 2 | `asod_line` | int(10,0) | NO |
| 3 | `asod_src_nbr` | varchar(15) | NO |
| 4 | `asod_src_line` | int(10,0) | NO |
| 5 | `asod_part` | varchar(30) | NO |
| 6 | `asod_qty` | numeric(19,8) | NO |
| 7 | `asod_loc` | varchar(8) | NO |
| 8 | `asod_lot` | varchar(18) | NO |
| 9 | `asod_rmks` | varchar(255) | NO |
| 10 | `asod_crt_by` | varchar(12) | NO |
| 11 | `asod_crt_date` | datetime | NO |
| 12 | `asod_mod_times` | int(10,0) | NO |
| 13 | `asod_mod_by` | varchar(12) | NO |
| 14 | `asod_mod_date` | datetime | NO |
| 15 | `asod_char1` | varchar(255) | NO |
| 16 | `asod_char2` | varchar(255) | NO |
| 17 | `asod_char3` | varchar(255) | NO |
| 18 | `asod_char4` | varchar(255) | NO |
| 19 | `asod_char5` | varchar(255) | NO |
| 20 | `asod_char6` | varchar(255) | NO |
| 21 | `asod_qty1` | decimal(19,8) | NO |
| 22 | `asod_qty2` | decimal(19,8) | NO |
| 23 | `asod_src_seq` | int(10,0) | NO |

### `dbo.asq_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asq_nbr` | varchar(15) | NO |
| 2 | `asq_date` | datetime | NO |
| 3 | `asq_rmks` | varchar(255) | NO |
| 4 | `asq_site` | varchar(8) | NO |
| 5 | `asq_wf_status` | varchar(1) | NO |
| 6 | `asq_prog_code` | varchar(12) | NO |
| 7 | `asq_crt_by` | varchar(12) | NO |
| 8 | `asq_crt_date` | datetime | NO |
| 9 | `asq_mod_times` | int(10,0) | NO |
| 10 | `asq_mod_by` | varchar(12) | NO |
| 11 | `asq_mod_date` | datetime | NO |
| 12 | `asq_pst` | bit | NO |
| 13 | `asq_pst_by` | varchar(12) | NO |
| 14 | `asq_pst_date` | datetime | YES |
| 15 | `asq_chk` | bit | NO |
| 16 | `asq_chk_by` | varchar(12) | NO |
| 17 | `asq_chk_date` | datetime | YES |
| 18 | `asq_char1` | varchar(255) | NO |
| 19 | `asq_char2` | varchar(255) | NO |
| 20 | `asq_char3` | varchar(255) | NO |
| 21 | `asq_char4` | varchar(255) | NO |
| 22 | `asq_char5` | varchar(255) | NO |
| 23 | `asq_char6` | varchar(255) | NO |
| 24 | `asq_qty1` | decimal(19,8) | NO |
| 25 | `asq_qty2` | decimal(19,8) | NO |

### `dbo.asqd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asqd_nbr` | varchar(15) | NO |
| 2 | `asqd_line` | int(10,0) | NO |
| 3 | `asqd_src_nbr` | varchar(15) | NO |
| 4 | `asqd_src_line` | int(10,0) | NO |
| 5 | `asqd_part` | varchar(30) | NO |
| 6 | `asqd_qty` | numeric(19,8) | NO |
| 7 | `asqd_can_fix` | bit | NO |
| 8 | `asqd_reason` | varchar(255) | NO |
| 9 | `asqd_deal_type` | varchar(1) | NO |
| 10 | `asqd_loc` | varchar(8) | NO |
| 11 | `asqd_lot` | varchar(18) | NO |
| 12 | `asqd_rmks` | varchar(255) | NO |
| 13 | `asqd_crt_by` | varchar(12) | NO |
| 14 | `asqd_crt_date` | datetime | NO |
| 15 | `asqd_mod_times` | int(10,0) | NO |
| 16 | `asqd_mod_by` | varchar(12) | NO |
| 17 | `asqd_mod_date` | datetime | NO |
| 18 | `asqd_char1` | varchar(255) | NO |
| 19 | `asqd_char2` | varchar(255) | NO |
| 20 | `asqd_char3` | varchar(255) | NO |
| 21 | `asqd_char4` | varchar(255) | NO |
| 22 | `asqd_char5` | varchar(255) | NO |
| 23 | `asqd_char6` | varchar(255) | NO |
| 24 | `asqd_qty1` | decimal(19,8) | NO |
| 25 | `asqd_qty2` | decimal(19,8) | NO |
| 26 | `asqd_need_fix` | bit | NO |

### `dbo.asqd2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asqd2_nbr` | varchar(15) | NO |
| 2 | `asqd2_line` | int(10,0) | NO |
| 3 | `asqd2_seq` | int(10,0) | NO |
| 4 | `asqd2_part` | varchar(30) | NO |
| 5 | `asqd2_loss_item` | varchar(30) | NO |
| 6 | `asqd2_qty` | numeric(19,8) | NO |
| 7 | `asqd2_qty_iss` | numeric(19,8) | NO |
| 8 | `asqd2_price` | numeric(19,8) | NO |
| 9 | `asqd2_rmks` | varchar(255) | NO |
| 10 | `asqd2_crt_by` | varchar(12) | NO |
| 11 | `asqd2_crt_date` | datetime | NO |
| 12 | `asqd2_mod_times` | int(10,0) | NO |
| 13 | `asqd2_mod_by` | varchar(12) | NO |
| 14 | `asqd2_mod_date` | datetime | NO |
| 15 | `asqd2_char1` | varchar(255) | NO |
| 16 | `asqd2_char2` | varchar(255) | NO |
| 17 | `asqd2_char3` | varchar(255) | NO |
| 18 | `asqd2_char4` | varchar(255) | NO |
| 19 | `asqd2_char5` | varchar(255) | NO |
| 20 | `asqd2_char6` | varchar(255) | NO |
| 21 | `asqd2_qty1` | decimal(19,8) | NO |
| 22 | `asqd2_qty2` | decimal(19,8) | NO |

### `dbo.auto_pfb` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `auto_user` | varchar(12) | NO |
| 2 | `auto_flow` | int(10,0) | NO |
| 3 | `auto_selected` | bit | NO |
| 4 | `auto_dpmd_nbr` | varchar(15) | NO |
| 5 | `auto_dpmd_line` | int(10,0) | NO |
| 6 | `auto_wr_nbr` | varchar(15) | NO |
| 7 | `auto_wr_lot` | varchar(18) | NO |
| 8 | `auto_wr_op` | int(10,0) | NO |
| 9 | `auto_wr_desc` | varchar(255) | NO |
| 10 | `auto_wkctr` | varchar(8) | NO |
| 11 | `auto_emp` | varchar(12) | NO |
| 12 | `auto_part` | varchar(30) | NO |
| 13 | `auto_qty_ord` | numeric(19,8) | NO |
| 14 | `auto_qty_comp` | numeric(19,8) | NO |
| 15 | `auto_qty_rjct` | numeric(19,8) | NO |
| 16 | `auto_start_date` | datetime | YES |
| 17 | `auto_start_time` | varchar(10) | NO |
| 18 | `auto_stop_date` | datetime | YES |
| 19 | `auto_stop_time` | varchar(10) | NO |
| 20 | `auto_used_time` | numeric(19,8) | NO |
| 21 | `auto_rmks` | varchar(255) | NO |
| 22 | `auto_char1` | varchar(255) | NO |
| 23 | `auto_char2` | varchar(255) | NO |
| 24 | `auto_char3` | varchar(255) | NO |
| 25 | `auto_char4` | varchar(255) | NO |
| 26 | `auto_char5` | varchar(255) | NO |
| 27 | `auto_char6` | varchar(255) | NO |
| 28 | `auto_qty1` | decimal(19,8) | NO |
| 29 | `auto_qty2` | decimal(19,8) | NO |

### `dbo.auto_po` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `auto_user` | varchar(12) | NO |
| 2 | `auto_flow` | int(10,0) | NO |
| 3 | `auto_vend` | varchar(8) | NO |
| 4 | `auto_part` | varchar(30) | NO |
| 5 | `auto_curr` | varchar(4) | NO |
| 6 | `auto_vat` | decimal(19,8) | NO |
| 7 | `auto_qty` | numeric(19,8) | NO |
| 8 | `auto_qty_tot` | numeric(19,8) | NO |
| 9 | `auto_price_old` | decimal(19,8) | NO |
| 10 | `auto_price_new` | decimal(19,8) | NO |

### `dbo.auto_tsfd1` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp1_user` | varchar(12) | NO |
| 2 | `tmp1_selected` | bit | NO |
| 3 | `tmp1_flow` | int(10,0) | NO |
| 4 | `tmp1_wo_nbr` | varchar(15) | NO |
| 5 | `tmp1_wo_lot` | varchar(18) | NO |
| 6 | `tmp1_wo_part` | varchar(30) | NO |
| 7 | `tmp1_wo_line` | varchar(8) | NO |
| 8 | `tmp1_wo_qty_ord` | numeric(19,8) | NO |
| 9 | `tmp1_wo_qty_comp` | numeric(19,8) | NO |
| 10 | `tmp1_wo_rel_date` | datetime | NO |
| 11 | `tmp1_wo_due_date` | datetime | NO |
| 12 | `tmp1_wo_max_qty` | numeric(19,8) | NO |
| 13 | `tmp1_wo_qty` | numeric(19,8) | NO |
| 14 | `tmp1_wo_rmks` | varchar(255) | NO |
| 15 | `tmp1_wo_so_nbr` | varchar(15) | NO |
| 16 | `tmp1_wo_so_line` | int(10,0) | NO |
| 17 | `tmp1_so_cust` | varchar(8) | NO |
| 18 | `tmp1_cm_sort` | varchar(50) | NO |

### `dbo.auto_tsfd2` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp2_user` | varchar(12) | NO |
| 2 | `tmp2_selected` | bit | NO |
| 3 | `tmp2_part` | varchar(30) | NO |
| 4 | `tmp2_seq` | int(10,0) | NO |
| 5 | `tmp2_wo_nbr` | varchar(15) | NO |
| 6 | `tmp2_wo_lot` | varchar(18) | NO |
| 7 | `tmp2_wo_seq` | int(10,0) | NO |
| 8 | `tmp2_wo_part` | varchar(30) | NO |
| 9 | `tmp2_wo_line` | varchar(8) | NO |
| 10 | `tmp2_wo_qty_ord` | numeric(19,8) | NO |
| 11 | `tmp2_wo_qty_comp` | numeric(19,8) | NO |
| 12 | `tmp2_wo_rel_date` | datetime | NO |
| 13 | `tmp2_wo_due_date` | datetime | NO |
| 14 | `tmp2_wo_qty_req` | numeric(19,8) | NO |
| 15 | `tmp2_wo_qty_iss` | numeric(19,8) | NO |
| 16 | `tmp2_wo_iss_unpst` | numeric(19,8) | NO |
| 17 | `tmp2_qty_alloc` | numeric(19,8) | NO |
| 18 | `tmp2_wo_rmks` | varchar(255) | NO |
| 19 | `tmp2_wo_so_nbr` | varchar(15) | NO |
| 20 | `tmp2_wo_so_line` | int(10,0) | NO |
| 21 | `tmp2_so_cust` | varchar(8) | NO |
| 22 | `tmp2_cm_sort` | varchar(50) | NO |

### `dbo.auto_wo` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `r_user_id` | varchar(12) | NO |
| 2 | `r_flow_no` | int(10,0) | NO |
| 3 | `r_site` | varchar(8) | NO |
| 4 | `r_conv_wo` | bit | NO |
| 5 | `r_conv_sc` | bit | NO |
| 6 | `r_prog_code` | varchar(12) | NO |
| 7 | `r_so_nbr` | varchar(15) | NO |
| 8 | `r_sod_line` | int(10,0) | NO |
| 9 | `r_part` | varchar(30) | NO |
| 10 | `r_qty_ord` | numeric(19,8) | NO |
| 11 | `r_qty_oh_avail` | numeric(19,8) | NO |
| 12 | `r_qty_req` | numeric(19,8) | NO |
| 13 | `r_qty_on_pr` | numeric(19,8) | NO |
| 14 | `r_qty_on_ord` | numeric(19,8) | NO |
| 15 | `r_qty_on_wip` | numeric(19,8) | NO |
| 16 | `r_qty_safty` | numeric(19,8) | NO |
| 17 | `r_qty_conv` | numeric(19,8) | NO |
| 18 | `r_qty_conv_o` | numeric(19,8) | NO |
| 19 | `r_wo_nbr` | varchar(15) | NO |
| 20 | `r_wo_lot` | varchar(18) | NO |
| 21 | `r_wo_line` | varchar(8) | NO |
| 22 | `r_due_date` | datetime | YES |
| 23 | `r_req_date` | datetime | YES |
| 24 | `r_master` | bit | NO |
| 25 | `r_mst_wo_nbr` | varchar(15) | NO |
| 26 | `r_mst_wo_lot` | varchar(18) | NO |

### `dbo.auto_wo2` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `r_flow_no` | int(10,0) | NO |
| 2 | `r_user_id` | varchar(12) | NO |
| 3 | `r_conv_wo` | bit | NO |
| 4 | `r_so_nbr` | varchar(15) | NO |
| 5 | `r_sod_line` | int(10,0) | NO |
| 6 | `r_part` | varchar(30) | NO |
| 7 | `r_qty_ord` | numeric(19,8) | NO |
| 8 | `r_qty_oh_avail` | numeric(19,8) | NO |
| 9 | `r_qty_req` | numeric(19,8) | NO |
| 10 | `r_qty_on_pr` | numeric(19,8) | NO |
| 11 | `r_qty_on_ord` | numeric(19,8) | NO |
| 12 | `r_qty_on_wip` | numeric(19,8) | NO |
| 13 | `r_qty_safty` | numeric(19,8) | NO |
| 14 | `r_qty_conv` | numeric(19,8) | NO |
| 15 | `r_qty_conv_o` | numeric(19,8) | NO |
| 16 | `r_wo_nbr` | varchar(15) | NO |
| 17 | `r_wo_lot` | varchar(18) | NO |
| 18 | `r_wo_line` | varchar(8) | NO |
| 19 | `r_due_date` | datetime | NO |
| 20 | `r_req_date` | datetime | NO |
| 21 | `r_ord_date` | datetime | NO |
| 22 | `r_qty_per_nbr` | numeric(19,8) | NO |
| 23 | `r_days` | int(10,0) | NO |
| 24 | `r_rtn_flag` | bit | NO |
| 25 | `r_rtn_type` | varchar(1) | NO |
| 26 | `r_qty_conved` | numeric(19,8) | NO |

### `dbo.auto_woadj` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_user` | varchar(12) | NO |
| 2 | `tmp_flow` | int(10,0) | NO |
| 3 | `tmp_selected` | bit | NO |
| 4 | `tmp_line` | varchar(8) | NO |
| 5 | `tmp_wod_nbr` | varchar(15) | NO |
| 6 | `tmp_wod_lot` | varchar(18) | NO |
| 7 | `tmp_wod_seq` | int(10,0) | NO |
| 8 | `tmp_wod_part` | varchar(30) | NO |
| 9 | `tmp_qty_rec` | numeric(19,8) | NO |

### `dbo.auto_wtf1` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `aw_flow` | int(10,0) | NO |
| 2 | `aw_user_id` | varchar(12) | NO |
| 3 | `aw_selected` | bit | NO |
| 4 | `aw_wod_nbr` | varchar(15) | NO |
| 5 | `aw_wod_lot` | varchar(18) | NO |
| 6 | `aw_wod_seq` | int(10,0) | NO |
| 7 | `aw_wod_part` | varchar(30) | NO |
| 8 | `aw_wod_qty_req_std` | numeric(19,8) | NO |
| 9 | `aw_wod_qty_req_scr` | numeric(19,8) | NO |
| 10 | `aw_wod_qty_iss` | numeric(19,8) | NO |
| 11 | `aw_wod_qty_unpst` | numeric(19,8) | NO |
| 12 | `aw_wod_qty_rtng` | numeric(19,8) | NO |
| 13 | `aw_wod_qty_con` | numeric(19,8) | NO |
| 14 | `aw_qty_req` | numeric(19,8) | NO |
| 15 | `aw_qty_short` | numeric(19,8) | NO |
| 16 | `aw_qty_iss` | numeric(19,8) | NO |
| 17 | `aw_qty_ovr` | numeric(19,8) | NO |
| 18 | `aw_char1` | varchar(255) | NO |
| 19 | `aw_char2` | varchar(255) | NO |
| 20 | `aw_char3` | varchar(255) | NO |
| 21 | `aw_char4` | varchar(255) | NO |
| 22 | `aw_char5` | varchar(255) | NO |
| 23 | `aw_char6` | varchar(255) | NO |
| 24 | `aw_qty1` | decimal(19,8) | NO |
| 25 | `aw_qty2` | decimal(19,8) | NO |

### `dbo.auto_wtf2` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `aw2_flow` | int(10,0) | NO |
| 2 | `aw2_index` | int(10,0) | NO |
| 3 | `aw2_wod_nbr` | varchar(15) | NO |
| 4 | `aw2_wod_lot` | varchar(18) | NO |
| 5 | `aw2_wod_seq` | int(10,0) | NO |
| 6 | `aw2_wod_qty_req_std` | numeric(19,8) | NO |
| 7 | `aw2_wod_qty_req_scr` | numeric(19,8) | NO |
| 8 | `aw2_wod_qty_iss` | numeric(19,8) | NO |
| 9 | `aw2_wod_qty_unpst` | numeric(19,8) | NO |
| 10 | `aw2_wod_qty_rtng` | numeric(19,8) | NO |
| 11 | `aw2_wod_qty_con` | numeric(19,8) | NO |
| 12 | `aw2_qty_wip` | numeric(19,8) | NO |
| 13 | `aw2_qty_iss` | numeric(19,8) | NO |
| 14 | `aw2_qty_ovr` | numeric(19,8) | NO |
| 15 | `aw2_char1` | varchar(255) | NO |
| 16 | `aw2_char2` | varchar(255) | NO |
| 17 | `aw2_char3` | varchar(255) | NO |
| 18 | `aw2_char4` | varchar(255) | NO |
| 19 | `aw2_char5` | varchar(255) | NO |
| 20 | `aw2_char6` | varchar(255) | NO |
| 21 | `aw2_qty1` | decimal(19,8) | NO |
| 22 | `aw2_qty2` | decimal(19,8) | NO |

### `dbo.bg_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `bg_nbr` | varchar(15) | NO |
| 2 | `bg_year` | int(10,0) | NO |
| 3 | `bg_type` | varchar(30) | NO |
| 4 | `bg_scope` | varchar(1) | NO |
| 5 | `bg_ac_code` | varchar(15) | NO |
| 6 | `bg_dept` | varchar(10) | NO |
| 7 | `bg_amt` | numeric(19,8) | NO |
| 8 | `bg_rmks` | varchar(255) | NO |
| 9 | `bg_prog_code` | varchar(12) | NO |
| 10 | `bg_crt_by` | varchar(12) | NO |
| 11 | `bg_crt_date` | datetime | NO |
| 12 | `bg_mod_times` | int(10,0) | NO |
| 13 | `bg_mod_by` | varchar(12) | NO |
| 14 | `bg_mod_date` | datetime | NO |
| 15 | `bg_pst` | bit | NO |
| 16 | `bg_pst_by` | varchar(12) | NO |
| 17 | `bg_pst_date` | datetime | YES |
| 18 | `bg_char1` | varchar(255) | NO |
| 19 | `bg_char2` | varchar(255) | NO |
| 20 | `bg_char3` | varchar(255) | NO |
| 21 | `bg_char4` | varchar(255) | NO |
| 22 | `bg_char5` | varchar(255) | NO |
| 23 | `bg_char6` | varchar(255) | NO |
| 24 | `bg_qty1` | decimal(19,8) | NO |
| 25 | `bg_qty2` | decimal(19,8) | NO |

### `dbo.bgd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `bgd_nbr` | varchar(15) | NO |
| 2 | `bgd_line` | int(10,0) | NO |
| 3 | `bgd_dept` | varchar(10) | NO |
| 4 | `bgd_month` | int(10,0) | NO |
| 5 | `bgd_amt` | numeric(19,8) | NO |
| 6 | `bgd_rmks` | varchar(255) | NO |
| 7 | `bgd_crt_by` | varchar(12) | NO |
| 8 | `bgd_crt_date` | datetime | NO |
| 9 | `bgd_mod_times` | int(10,0) | NO |
| 10 | `bgd_mod_by` | varchar(12) | NO |
| 11 | `bgd_mod_date` | datetime | NO |
| 12 | `bgd_char1` | varchar(255) | NO |
| 13 | `bgd_char2` | varchar(255) | NO |
| 14 | `bgd_char3` | varchar(255) | NO |
| 15 | `bgd_char4` | varchar(255) | NO |
| 16 | `bgd_char5` | varchar(255) | NO |
| 17 | `bgd_char6` | varchar(255) | NO |
| 18 | `bgd_qty1` | decimal(19,8) | NO |
| 19 | `bgd_qty2` | decimal(19,8) | NO |

### `dbo.ca_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ca_cust` | varchar(8) | NO |
| 2 | `ca_addr` | varchar(8) | NO |
| 3 | `ca_txt` | varchar(255) | NO |
| 4 | `ca_rmks` | varchar(255) | NO |
| 5 | `ca_crt_by` | varchar(12) | NO |
| 6 | `ca_crt_date` | datetime | NO |
| 7 | `ca_char1` | varchar(255) | NO |
| 8 | `ca_char2` | varchar(255) | NO |
| 9 | `ca_char3` | varchar(255) | NO |
| 10 | `ca_char4` | varchar(255) | NO |
| 11 | `ca_char5` | varchar(255) | NO |
| 12 | `ca_char6` | varchar(255) | NO |
| 13 | `ca_qty1` | decimal(19,8) | NO |
| 14 | `ca_qty2` | decimal(19,8) | NO |

### `dbo.caj_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `caj_nbr` | varchar(15) | NO |
| 2 | `caj_date` | datetime | NO |
| 3 | `caj_rmks` | varchar(255) | NO |
| 4 | `caj_site` | varchar(8) | NO |
| 5 | `caj_prog_code` | varchar(12) | NO |
| 6 | `caj_doc_code` | varchar(12) | NO |
| 7 | `caj_wf_status` | varchar(1) | NO |
| 8 | `caj_crt_by` | varchar(12) | NO |
| 9 | `caj_crt_date` | datetime | NO |
| 10 | `caj_mod_times` | int(10,0) | NO |
| 11 | `caj_mod_by` | varchar(12) | NO |
| 12 | `caj_mod_date` | datetime | NO |
| 13 | `caj_pst` | bit | NO |
| 14 | `caj_pst_by` | varchar(12) | NO |
| 15 | `caj_pst_date` | datetime | YES |
| 16 | `caj_char1` | varchar(255) | NO |
| 17 | `caj_char2` | varchar(255) | NO |
| 18 | `caj_char3` | varchar(255) | NO |
| 19 | `caj_char4` | varchar(255) | NO |
| 20 | `caj_char5` | varchar(255) | NO |
| 21 | `caj_char6` | varchar(255) | NO |
| 22 | `caj_qty1` | decimal(19,8) | NO |
| 23 | `caj_qty2` | decimal(19,8) | NO |

### `dbo.cajd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cajd_nbr` | varchar(15) | NO |
| 2 | `cajd_line` | int(10,0) | NO |
| 3 | `cajd_part` | varchar(30) | NO |
| 4 | `cajd_loc` | varchar(8) | NO |
| 5 | `cajd_lot` | varchar(18) | NO |
| 6 | `cajd_qty_old` | numeric(19,8) | NO |
| 7 | `cajd_mtl_old` | decimal(19,8) | NO |
| 8 | `cajd_lbr_old` | decimal(19,8) | NO |
| 9 | `cajd_bdn_old` | decimal(19,8) | NO |
| 10 | `cajd_sub_old` | decimal(19,8) | NO |
| 11 | `cajd_mtl_ll_old` | decimal(19,8) | NO |
| 12 | `cajd_lbr_ll_old` | decimal(19,8) | NO |
| 13 | `cajd_bdn_ll_old` | decimal(19,8) | NO |
| 14 | `cajd_sub_ll_old` | decimal(19,8) | NO |
| 15 | `cajd_mtl_new` | decimal(19,8) | NO |
| 16 | `cajd_lbr_new` | decimal(19,8) | NO |
| 17 | `cajd_bdn_new` | decimal(19,8) | NO |
| 18 | `cajd_sub_new` | decimal(19,8) | NO |
| 19 | `cajd_mtl_ll_new` | decimal(19,8) | NO |
| 20 | `cajd_lbr_ll_new` | decimal(19,8) | NO |
| 21 | `cajd_bdn_ll_new` | decimal(19,8) | NO |
| 22 | `cajd_sub_ll_new` | decimal(19,8) | NO |
| 23 | `cajd_char1` | varchar(255) | NO |
| 24 | `cajd_char2` | varchar(255) | NO |
| 25 | `cajd_char3` | varchar(255) | NO |
| 26 | `cajd_char4` | varchar(255) | NO |
| 27 | `cajd_char5` | varchar(255) | NO |
| 28 | `cajd_char6` | varchar(255) | NO |
| 29 | `cajd_qty1` | decimal(19,8) | NO |
| 30 | `cajd_qty2` | decimal(19,8) | NO |

### `dbo.capf_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `capf_flow` | int(10,0) | NO |
| 2 | `capf_date` | datetime | NO |
| 3 | `capf_ac_code` | varchar(15) | NO |
| 4 | `capf_bank` | varchar(255) | NO |
| 5 | `capf_account` | varchar(255) | NO |
| 6 | `capf_d_c` | varchar(1) | NO |
| 7 | `capf_opp_name` | varchar(255) | NO |
| 8 | `capf_curr` | varchar(4) | NO |
| 9 | `capf_amt` | numeric(19,8) | NO |
| 10 | `capf_amt_used` | numeric(19,8) | NO |
| 11 | `capf_closed` | bit | NO |
| 12 | `capf_content` | varchar(255) | NO |
| 13 | `capf_rmks` | varchar(255) | NO |
| 14 | `capf_crt_by` | varchar(12) | NO |
| 15 | `capf_crt_date` | datetime | NO |
| 16 | `capf_mod_times` | int(10,0) | NO |
| 17 | `capf_mod_by` | varchar(12) | NO |
| 18 | `capf_mod_date` | datetime | NO |
| 19 | `capf_pst` | bit | NO |
| 20 | `capf_pst_by` | varchar(12) | NO |
| 21 | `capf_pst_date` | datetime | YES |
| 22 | `capf_char1` | varchar(255) | NO |
| 23 | `capf_char2` | varchar(255) | NO |
| 24 | `capf_char3` | varchar(255) | NO |
| 25 | `capf_char4` | varchar(255) | NO |
| 26 | `capf_char5` | varchar(255) | NO |
| 27 | `capf_char6` | varchar(255) | NO |
| 28 | `capf_qty1` | decimal(19,8) | NO |
| 29 | `capf_qty2` | decimal(19,8) | NO |
| 30 | `capf_qty3` | decimal(19,8) | NO |
| 31 | `capf_qty4` | decimal(19,8) | NO |
| 32 | `capf_qty5` | decimal(19,8) | NO |
| 33 | `capf_qty6` | decimal(19,8) | NO |

### `dbo.cashf_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cashf_vch_nbr` | varchar(15) | NO |
| 2 | `cashf_vch_vt_code` | varchar(15) | NO |
| 3 | `cashf_vch_date` | datetime | NO |
| 4 | `cashf_vchd_line` | int(10,0) | NO |
| 5 | `cashf_ac_code` | varchar(15) | NO |
| 6 | `cashf_d_c` | varchar(1) | NO |
| 7 | `cashf_curr` | varchar(4) | NO |
| 8 | `cashf_amt` | numeric(19,8) | NO |
| 9 | `cashf_amt_base` | numeric(19,8) | NO |
| 10 | `cashf_item` | varchar(4) | NO |
| 11 | `cashf_cashac_code` | varchar(15) | NO |
| 12 | `cashf_content` | varchar(255) | NO |
| 13 | `cashf_rmks` | varchar(255) | NO |
| 14 | `cashf_vt_code1` | varchar(30) | NO |
| 15 | `cashf_vt_name1` | varchar(255) | NO |
| 16 | `cashf_vt_code2` | varchar(30) | NO |
| 17 | `cashf_vt_name2` | varchar(255) | NO |
| 18 | `cashf_vt_code3` | varchar(30) | NO |
| 19 | `cashf_vt_name3` | varchar(255) | NO |
| 20 | `cashf_vt_code4` | varchar(30) | NO |
| 21 | `cashf_vt_name4` | varchar(255) | NO |
| 22 | `cashf_char1` | varchar(255) | NO |
| 23 | `cashf_char2` | varchar(255) | NO |
| 24 | `cashf_char3` | varchar(255) | NO |
| 25 | `cashf_char4` | varchar(255) | NO |
| 26 | `cashf_char5` | varchar(255) | NO |
| 27 | `cashf_char6` | varchar(255) | NO |
| 28 | `cashf_qty1` | decimal(19,8) | NO |
| 29 | `cashf_qty2` | decimal(19,8) | NO |

### `dbo.cend_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cend_nbr` | varchar(15) | NO |
| 2 | `cend_line` | int(10,0) | NO |
| 3 | `cend_d_c` | varchar(1) | NO |
| 4 | `cend_ac_code` | varchar(15) | NO |
| 5 | `cend_curr` | varchar(4) | NO |
| 6 | `cend_exch_rate` | decimal(19,8) | NO |
| 7 | `cend_amt` | decimal(19,8) | NO |
| 8 | `cend_amt_base` | decimal(19,8) | NO |
| 9 | `cend_tr_type` | varchar(8) | NO |
| 10 | `cend_ref_nbr` | varchar(15) | NO |
| 11 | `cend_ref_line` | int(10,0) | NO |
| 12 | `cend_doc_date` | datetime | YES |
| 13 | `cend_part` | varchar(30) | NO |
| 14 | `cend_qty` | numeric(19,8) | NO |
| 15 | `cend_um` | varchar(4) | NO |
| 16 | `cend_doc_nbr` | varchar(15) | NO |
| 17 | `cend_mtl_cost` | decimal(19,8) | NO |
| 18 | `cend_lbr_cost` | decimal(19,8) | NO |
| 19 | `cend_bdn_cost` | decimal(19,8) | NO |
| 20 | `cend_sub_cost` | decimal(19,8) | NO |
| 21 | `cend_cm_vd` | varchar(8) | NO |
| 22 | `cend_ar_nbr` | varchar(15) | NO |
| 23 | `cend_dept` | varchar(30) | NO |
| 24 | `cend_rmks` | varchar(255) | NO |
| 25 | `cend_crt_by` | varchar(12) | NO |
| 26 | `cend_crt_date` | datetime | NO |
| 27 | `cend_mod_times` | int(10,0) | NO |
| 28 | `cend_mod_by` | varchar(12) | NO |
| 29 | `cend_mod_date` | datetime | NO |
| 30 | `cend_char1` | varchar(255) | NO |
| 31 | `cend_char2` | varchar(255) | NO |
| 32 | `cend_char3` | varchar(255) | NO |
| 33 | `cend_char4` | varchar(255) | NO |
| 34 | `cend_char5` | varchar(255) | NO |
| 35 | `cend_char6` | varchar(255) | NO |
| 36 | `cend_qty1` | decimal(19,8) | NO |
| 37 | `cend_qty2` | decimal(19,8) | NO |
| 38 | `cend_crt_name` | varchar(30) | NO |
| 39 | `cend_mod_name` | varchar(30) | NO |

### `dbo.cf_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cf_nbr` | varchar(15) | NO |
| 2 | `cf_date` | datetime | NO |
| 3 | `cf_cust` | varchar(8) | NO |
| 4 | `cf_curr` | varchar(4) | NO |
| 5 | `cf_vat` | decimal(19,8) | NO |
| 6 | `cf_ex_rate` | decimal(19,8) | NO |
| 7 | `cf_rmks` | varchar(255) | NO |
| 8 | `cf_site` | varchar(8) | NO |
| 9 | `cf_prog_code` | varchar(12) | NO |
| 10 | `cf_wf_status` | varchar(1) | NO |
| 11 | `cf_crt_by` | varchar(12) | NO |
| 12 | `cf_crt_date` | datetime | NO |
| 13 | `cf_mod_times` | int(10,0) | NO |
| 14 | `cf_mod_by` | varchar(12) | NO |
| 15 | `cf_mod_date` | datetime | NO |
| 16 | `cf_pst` | bit | NO |
| 17 | `cf_pst_by` | varchar(12) | NO |
| 18 | `cf_pst_date` | datetime | YES |
| 19 | `cf_char1` | varchar(255) | NO |
| 20 | `cf_char2` | varchar(255) | NO |
| 21 | `cf_char3` | varchar(255) | NO |
| 22 | `cf_char4` | varchar(255) | NO |
| 23 | `cf_char5` | varchar(255) | NO |
| 24 | `cf_char6` | varchar(255) | NO |
| 25 | `cf_qty1` | decimal(19,8) | NO |
| 26 | `cf_qty2` | decimal(19,8) | NO |

### `dbo.cfd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cfd_nbr` | varchar(15) | NO |
| 2 | `cfd_line` | int(10,0) | NO |
| 3 | `cfd_part` | varchar(30) | NO |
| 4 | `cfd_desc` | varchar(255) | NO |
| 5 | `cfd_amt` | numeric(19,8) | NO |
| 6 | `cfd_so` | varchar(15) | NO |
| 7 | `cfd_rmks` | varchar(255) | NO |
| 8 | `cfd_crt_by` | varchar(12) | NO |
| 9 | `cfd_crt_date` | datetime | NO |
| 10 | `cfd_mod_times` | int(10,0) | NO |
| 11 | `cfd_mod_by` | varchar(12) | NO |
| 12 | `cfd_mod_date` | datetime | NO |
| 13 | `cfd_char1` | varchar(255) | NO |
| 14 | `cfd_char2` | varchar(255) | NO |
| 15 | `cfd_char3` | varchar(255) | NO |
| 16 | `cfd_char4` | varchar(255) | NO |
| 17 | `cfd_char5` | varchar(255) | NO |
| 18 | `cfd_char6` | varchar(255) | NO |
| 19 | `cfd_qty1` | decimal(19,8) | NO |
| 20 | `cfd_qty2` | decimal(19,8) | NO |
| 21 | `cfd_qty` | numeric(19,8) | NO |
| 22 | `cfd_price` | decimal(19,8) | NO |
| 23 | `cfd_curr` | varchar(4) | NO |
| 24 | `cfd_ex_rate` | numeric(19,8) | NO |
| 25 | `cfd_vat` | numeric(19,8) | NO |

### `dbo.chk_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `chk_user` | varchar(12) | NO |
| 2 | `chk_loc` | varchar(8) | NO |
| 3 | `chk_part` | varchar(30) | NO |
| 4 | `chk_lot` | varchar(18) | NO |
| 5 | `chk_qty` | numeric(19,8) | NO |
| 6 | `chk_char1` | varchar(255) | NO |
| 7 | `chk_char2` | varchar(255) | NO |
| 8 | `chk_char3` | varchar(255) | NO |
| 9 | `chk_char4` | varchar(255) | NO |
| 10 | `chk_char5` | varchar(255) | NO |
| 11 | `chk_char6` | varchar(255) | NO |
| 12 | `chk_qty1` | decimal(19,8) | NO |
| 13 | `chk_qty2` | decimal(19,8) | NO |

### `dbo.cid_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cid_code` | varchar(4) | NO |
| 2 | `cid_item` | varchar(4) | NO |
| 3 | `cid_name` | varchar(255) | NO |
| 4 | `cid_crt_by` | varchar(12) | NO |
| 5 | `cid_crt_date` | datetime | NO |
| 6 | `cid_mod_times` | int(10,0) | NO |
| 7 | `cid_mod_by` | varchar(12) | NO |
| 8 | `cid_mod_date` | datetime | NO |
| 9 | `cid_char1` | varchar(255) | NO |
| 10 | `cid_char2` | varchar(255) | NO |
| 11 | `cid_char3` | varchar(255) | NO |
| 12 | `cid_char4` | varchar(255) | NO |
| 13 | `cid_char5` | varchar(255) | NO |
| 14 | `cid_char6` | varchar(255) | NO |
| 15 | `cid_qty1` | decimal(19,8) | NO |
| 16 | `cid_qty2` | decimal(19,8) | NO |

### `dbo.cinv_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cinv_nbr` | varchar(15) | NO |
| 2 | `cinv_cust` | varchar(8) | NO |
| 3 | `cinv_eff_date` | datetime | NO |
| 4 | `cinv_due_date` | datetime | NO |
| 5 | `cinv_disc_date` | datetime | NO |
| 6 | `cinv_cr_terms` | varchar(10) | NO |
| 7 | `cinv_disc` | decimal(19,8) | NO |
| 8 | `cinv_curr` | varchar(4) | NO |
| 9 | `cinv_shp_per` | varchar(30) | NO |
| 10 | `cinv_del_fr` | varchar(255) | NO |
| 11 | `cinv_del_to` | varchar(255) | NO |
| 12 | `cinv_sai_date` | datetime | YES |
| 13 | `cinv_lc_no` | varchar(50) | NO |
| 14 | `cinv_con_no` | varchar(50) | NO |
| 15 | `cinv_cun_org` | varchar(50) | NO |
| 16 | `cinv_sea_no` | varchar(50) | NO |
| 17 | `cinv_rmks` | varchar(255) | NO |
| 18 | `cinv_site` | varchar(8) | NO |
| 19 | `cinv_prog_code` | varchar(12) | NO |
| 20 | `cinv_crt_by` | varchar(12) | NO |
| 21 | `cinv_crt_date` | datetime | NO |
| 22 | `cinv_mod_times` | int(10,0) | NO |
| 23 | `cinv_mod_by` | varchar(12) | NO |
| 24 | `cinv_mod_date` | datetime | NO |
| 25 | `cinv_pst` | bit | NO |
| 26 | `cinv_pst_by` | varchar(12) | NO |
| 27 | `cinv_pst_date` | datetime | YES |
| 28 | `cinv_char1` | varchar(255) | NO |
| 29 | `cinv_char2` | varchar(255) | NO |
| 30 | `cinv_char3` | varchar(255) | NO |
| 31 | `cinv_char4` | varchar(255) | NO |
| 32 | `cinv_char5` | varchar(255) | NO |
| 33 | `cinv_char6` | varchar(255) | NO |
| 34 | `cinv_qty1` | decimal(19,8) | NO |
| 35 | `cinv_qty2` | decimal(19,8) | NO |

### `dbo.cm_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cm_addr` | varchar(8) | NO |
| 2 | `cm_name` | varchar(255) | NO |
| 3 | `cm_sort` | varchar(50) | NO |
| 4 | `cm_txt_inv` | varchar(255) | NO |
| 5 | `cm_txt_run` | varchar(255) | NO |
| 6 | `cm_txt_ship` | varchar(255) | NO |
| 7 | `cm_www` | varchar(80) | NO |
| 8 | `cm_attn1` | varchar(24) | NO |
| 9 | `cm_pos1` | varchar(30) | NO |
| 10 | `cm_tele1` | varchar(50) | NO |
| 11 | `cm_fax1` | varchar(50) | NO |
| 12 | `cm_email1` | varchar(50) | NO |
| 13 | `cm_attn2` | varchar(24) | NO |
| 14 | `cm_pos2` | varchar(30) | NO |
| 15 | `cm_tele2` | varchar(50) | NO |
| 16 | `cm_fax2` | varchar(50) | NO |
| 17 | `cm_email2` | varchar(50) | NO |
| 18 | `cm_attn3` | varchar(24) | NO |
| 19 | `cm_pos3` | varchar(30) | NO |
| 20 | `cm_tele3` | varchar(50) | NO |
| 21 | `cm_fax3` | varchar(50) | NO |
| 22 | `cm_email3` | varchar(50) | NO |
| 23 | `cm_attn4` | varchar(24) | NO |
| 24 | `cm_tele4` | varchar(50) | NO |
| 25 | `cm_fax4` | varchar(50) | NO |
| 26 | `cm_email4` | varchar(50) | NO |
| 27 | `cm_pos4` | varchar(30) | NO |
| 28 | `cm_cmmt` | varchar(255) | NO |
| 29 | `cm_slspsn` | varchar(12) | NO |
| 30 | `cm_kind` | varchar(1) | NO |
| 31 | `cm_type` | varchar(30) | NO |
| 32 | `cm_region` | varchar(30) | NO |
| 33 | `cm_quot_type` | varchar(1) | NO |
| 34 | `cm_vat_method` | varchar(1) | NO |
| 35 | `cm_cr_terms` | varchar(10) | NO |
| 36 | `cm_chk_day` | int(10,0) | NO |
| 37 | `cm_curr` | varchar(4) | NO |
| 38 | `cm_cr_hold` | bit | NO |
| 39 | `cm_disc` | decimal(19,8) | NO |
| 40 | `cm_vat` | decimal(19,8) | NO |
| 41 | `cm_spare_pct` | decimal(19,8) | NO |
| 42 | `cm_tol_pct` | decimal(19,8) | NO |
| 43 | `cm_consignment` | bit | NO |
| 44 | `cm_reg_code` | varchar(30) | NO |
| 45 | `cm_bank` | varchar(255) | NO |
| 46 | `cm_bank_acct` | varchar(30) | NO |
| 47 | `cm_comp_owner` | varchar(30) | NO |
| 48 | `cm_reg_fund` | decimal(19,8) | NO |
| 49 | `cm_tunrover` | decimal(19,8) | NO |
| 50 | `cm_open_date` | datetime | YES |
| 51 | `cm_employees` | int(10,0) | NO |
| 52 | `cm_limit_project` | varchar(30) | NO |
| 53 | `cm_credit1` | numeric(19,8) | NO |
| 54 | `cm_credit2` | numeric(19,8) | NO |
| 55 | `cm_max_days1` | int(10,0) | NO |
| 56 | `cm_max_days2` | int(10,0) | NO |
| 57 | `cm_ac_code_pre` | varchar(15) | NO |
| 58 | `cm_ac_code_ar` | varchar(15) | NO |
| 59 | `cm_ac_code_income` | varchar(15) | NO |
| 60 | `cm_ac_code_cost` | varchar(15) | NO |
| 61 | `cm_crt_by` | varchar(12) | NO |
| 62 | `cm_crt_date` | datetime | NO |
| 63 | `cm_mod_times` | int(10,0) | NO |
| 64 | `cm_mod_by` | varchar(12) | NO |
| 65 | `cm_mod_date` | datetime | NO |
| 66 | `cm_pst` | bit | NO |
| 67 | `cm_pst_by` | varchar(12) | NO |
| 68 | `cm_pst_date` | datetime | YES |
| 69 | `cm_wf_status` | varchar(1) | NO |
| 70 | `cm_char1` | varchar(255) | NO |
| 71 | `cm_char2` | varchar(255) | NO |
| 72 | `cm_char3` | varchar(255) | NO |
| 73 | `cm_char4` | varchar(255) | NO |
| 74 | `cm_char5` | varchar(255) | NO |
| 75 | `cm_char6` | varchar(255) | NO |
| 76 | `cm_qty1` | decimal(19,8) | NO |
| 77 | `cm_qty2` | decimal(19,8) | NO |
| 78 | `cm_ast_code` | varchar(15) | NO |
| 79 | `cm_headq` | varchar(8) | NO |
| 80 | `cm_dna_req` | bit | NO |
| 81 | `cm_invalid` | varchar(1) | NO |
| 82 | `cm_invalid_by` | varchar(12) | NO |
| 83 | `cm_invalid_date` | datetime | YES |
| 84 | `cm_ac_code_as` | varchar(15) | NO |
| 85 | `cm_cu_area` | varchar(30) | NO |
| 86 | `cm_cu_curr` | varchar(30) | NO |
| 87 | `cm_price_type` | varchar(1) | NO |
| 88 | `cm_inv_type` | varchar(1) | NO |
| 89 | `cm_tot_qty_price` | bit | NO |
| 90 | `cm_price_vat` | varchar(1) | NO |
| 91 | `cm_chk` | bit | NO |
| 92 | `cm_chk_by` | varchar(12) | NO |
| 93 | `cm_chk_date` | datetime | YES |
| 94 | `cm_template` | varchar(12) | NO |

### `dbo.code_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `code_code` | varchar(15) | NO |
| 2 | `code_site` | varchar(8) | NO |
| 3 | `code_company` | varchar(8) | NO |
| 4 | `code_prog_code` | varchar(12) | NO |
| 5 | `code_billtype` | varchar(15) | NO |
| 6 | `code_prefix` | varchar(8) | NO |
| 7 | `code_ylen` | int(10,0) | NO |
| 8 | `code_mlen` | int(10,0) | NO |
| 9 | `code_inc_day` | bit | NO |
| 10 | `code_datetype` | varchar(1) | NO |
| 11 | `code_flen` | int(10,0) | NO |
| 12 | `code_next` | int(10,0) | NO |
| 13 | `code_reset` | bit | NO |
| 14 | `code_empty_num` | bit | NO |
| 15 | `code_tablename` | varchar(50) | NO |
| 16 | `code_fldname` | varchar(50) | NO |
| 17 | `code_prompt` | bit | NO |
| 18 | `code_crt_by` | varchar(12) | NO |
| 19 | `code_crt_date` | datetime | NO |
| 20 | `code_char1` | varchar(255) | NO |
| 21 | `code_char2` | varchar(255) | NO |
| 22 | `code_char3` | varchar(255) | NO |
| 23 | `code_char4` | varchar(255) | NO |
| 24 | `code_char5` | varchar(255) | NO |
| 25 | `code_char6` | varchar(255) | NO |
| 26 | `code_qty1` | decimal(19,8) | NO |
| 27 | `code_qty2` | decimal(19,8) | NO |

### `dbo.cp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cp_cust` | varchar(8) | NO |
| 2 | `cp_part` | varchar(30) | NO |
| 3 | `cp_cust_part` | varchar(80) | NO |
| 4 | `cp_cust_desc` | varchar(255) | NO |
| 5 | `cp_um` | varchar(4) | NO |
| 6 | `cp_um_rate_m` | decimal(19,8) | NO |
| 7 | `cp_um_rate_d` | decimal(19,8) | NO |
| 8 | `cp_cmmt` | varchar(255) | NO |
| 9 | `cp_crt_by` | varchar(12) | NO |
| 10 | `cp_crt_date` | datetime | NO |
| 11 | `cp_char1` | varchar(255) | NO |
| 12 | `cp_char2` | varchar(255) | NO |
| 13 | `cp_char3` | varchar(255) | NO |
| 14 | `cp_char4` | varchar(255) | NO |
| 15 | `cp_char5` | varchar(255) | NO |
| 16 | `cp_char6` | varchar(255) | NO |
| 17 | `cp_qty1` | decimal(19,8) | NO |
| 18 | `cp_qty2` | decimal(19,8) | NO |

### `dbo.cpds_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cpds_cust` | varchar(8) | NO |
| 2 | `cpds_part` | varchar(30) | NO |
| 3 | `cpds_cust_part` | varchar(80) | NO |
| 4 | `cpds_db` | varchar(30) | NO |
| 5 | `cpds_db_desc` | varchar(255) | NO |
| 6 | `cpds_sync` | bit | NO |
| 7 | `cpds_rmks` | varchar(255) | NO |
| 8 | `cpds_crt_by` | varchar(12) | NO |
| 9 | `cpds_crt_name` | varchar(30) | NO |
| 10 | `cpds_crt_date` | datetime | NO |
| 11 | `cpds_mod_times` | int(10,0) | NO |
| 12 | `cpds_mod_by` | varchar(12) | NO |
| 13 | `cpds_mod_name` | varchar(30) | NO |
| 14 | `cpds_mod_date` | datetime | NO |
| 15 | `cpds_char1` | varchar(255) | NO |
| 16 | `cpds_char2` | varchar(255) | NO |
| 17 | `cpds_char3` | varchar(255) | NO |
| 18 | `cpds_char4` | varchar(255) | NO |
| 19 | `cpds_char5` | varchar(255) | NO |
| 20 | `cpds_char6` | varchar(255) | NO |
| 21 | `cpds_qty1` | decimal(19,8) | NO |
| 22 | `cpds_qty2` | decimal(19,8) | NO |

### `dbo.cpm_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cpm_company` | varchar(8) | NO |
| 2 | `cpm_nbr` | varchar(15) | NO |
| 3 | `cpm_doc_code` | varchar(15) | NO |
| 4 | `cpm_date` | datetime | NO |
| 5 | `cpm_customer` | varchar(8) | NO |
| 6 | `cpm_curr` | varchar(4) | NO |
| 7 | `cpm_rmks` | varchar(255) | NO |
| 8 | `cpm_vo_nbr` | varchar(15) | NO |
| 9 | `cpm_prn_cnt` | int(10,0) | NO |
| 10 | `cpm_base_debit_tot` | numeric(19,8) | NO |
| 11 | `cpm_base_credit_tot` | numeric(19,8) | NO |
| 12 | `cpm_prog_code` | varchar(12) | NO |
| 13 | `cpm_crt_by` | varchar(12) | NO |
| 14 | `cpm_crt_date` | datetime | NO |
| 15 | `cpm_mod_times` | int(10,0) | NO |
| 16 | `cpm_mod_by` | varchar(12) | NO |
| 17 | `cpm_mod_date` | datetime | NO |
| 18 | `cpm_pst` | bit | NO |
| 19 | `cpm_pst_by` | varchar(12) | NO |
| 20 | `cpm_pst_date` | datetime | YES |
| 21 | `cpm_char1` | varchar(255) | NO |
| 22 | `cpm_char2` | varchar(255) | NO |
| 23 | `cpm_char3` | varchar(255) | NO |
| 24 | `cpm_char4` | varchar(255) | NO |
| 25 | `cpm_char5` | varchar(255) | NO |
| 26 | `cpm_char6` | varchar(255) | NO |
| 27 | `cpm_qty1` | decimal(19,8) | NO |
| 28 | `cpm_qty2` | decimal(19,8) | NO |

### `dbo.cpmd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cpmd_nbr` | varchar(15) | NO |
| 2 | `cpmd_line` | int(10,0) | NO |
| 3 | `cpmd_d_c` | varchar(1) | NO |
| 4 | `cpmd_type` | varchar(1) | NO |
| 5 | `cpmd_src_doc` | varchar(15) | NO |
| 6 | `cpmd_src_nbr` | varchar(15) | NO |
| 7 | `cpmd_ac_code` | varchar(15) | NO |
| 8 | `cpmd_due_date` | datetime | YES |
| 9 | `cpmd_curr` | varchar(4) | NO |
| 10 | `cpmd_exch_rate` | decimal(19,8) | NO |
| 11 | `cpmd_last_exch_rate` | decimal(19,8) | NO |
| 12 | `cpmd_ar_amt` | numeric(19,8) | NO |
| 13 | `cpmd_open_amt` | numeric(19,8) | NO |
| 14 | `cpmd_pay_amt` | numeric(19,8) | NO |
| 15 | `cpmd_pay_base` | numeric(19,8) | NO |
| 16 | `cpmd_rmks` | varchar(255) | NO |
| 17 | `cpmd_dept` | varchar(10) | NO |
| 18 | `cpmd_analy1_code` | varchar(30) | NO |
| 19 | `cpmd_analy1_name` | varchar(255) | NO |
| 20 | `cpmd_analy2_code` | varchar(30) | NO |
| 21 | `cpmd_analy2_name` | varchar(255) | NO |
| 22 | `cpmd_analy3_code` | varchar(30) | NO |
| 23 | `cpmd_analy3_name` | varchar(255) | NO |
| 24 | `cpmd_analy4_code` | varchar(30) | NO |
| 25 | `cpmd_analy4_name` | varchar(255) | NO |
| 26 | `cpmd_crt_by` | varchar(12) | NO |
| 27 | `cpmd_crt_date` | datetime | NO |
| 28 | `cpmd_mod_times` | int(10,0) | NO |
| 29 | `cpmd_mod_by` | varchar(12) | NO |
| 30 | `cpmd_mod_date` | datetime | NO |
| 31 | `cpmd_char1` | varchar(255) | NO |
| 32 | `cpmd_char2` | varchar(255) | NO |
| 33 | `cpmd_char3` | varchar(255) | NO |
| 34 | `cpmd_char4` | varchar(255) | NO |
| 35 | `cpmd_char5` | varchar(255) | NO |
| 36 | `cpmd_char6` | varchar(255) | NO |
| 37 | `cpmd_qty1` | decimal(19,8) | NO |
| 38 | `cpmd_qty2` | decimal(19,8) | NO |
| 39 | `cpmd_capf_flow` | int(10,0) | NO |

### `dbo.cr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cr_cr` | varchar(15) | NO |
| 2 | `cr_date` | datetime | NO |
| 3 | `cr_cust` | varchar(8) | NO |
| 4 | `cr_loc` | varchar(8) | NO |
| 5 | `cr_replace` | bit | NO |
| 6 | `cr_type` | varchar(1) | NO |
| 7 | `cr_curr` | varchar(4) | NO |
| 8 | `cr_exch_rate` | decimal(19,8) | NO |
| 9 | `cr_vat` | decimal(19,8) | NO |
| 10 | `cr_rmks` | varchar(255) | NO |
| 11 | `cr_site` | varchar(8) | NO |
| 12 | `cr_wf_status` | varchar(1) | NO |
| 13 | `cr_prog_code` | varchar(12) | NO |
| 14 | `cr_doc_type` | varchar(12) | NO |
| 15 | `cr_crt_by` | varchar(12) | NO |
| 16 | `cr_crt_date` | datetime | NO |
| 17 | `cr_mod_times` | int(10,0) | NO |
| 18 | `cr_mod_by` | varchar(12) | NO |
| 19 | `cr_mod_date` | datetime | NO |
| 20 | `cr_pst` | bit | NO |
| 21 | `cr_pst_by` | varchar(12) | NO |
| 22 | `cr_pst_date` | datetime | YES |
| 23 | `cr_char1` | varchar(255) | NO |
| 24 | `cr_char2` | varchar(255) | NO |
| 25 | `cr_char3` | varchar(255) | NO |
| 26 | `cr_char4` | varchar(255) | NO |
| 27 | `cr_char5` | varchar(255) | NO |
| 28 | `cr_char6` | varchar(255) | NO |
| 29 | `cr_qty1` | decimal(19,8) | NO |
| 30 | `cr_qty2` | decimal(19,8) | NO |
| 31 | `cr_data_src` | varchar(1) | NO |
| 32 | `cr_data_id` | varchar(255) | NO |
| 33 | `cr_src` | varchar(2) | NO |
| 34 | `cr_src_nbr` | varchar(15) | NO |
| 35 | `cr_src_lot` | varchar(18) | NO |
| 36 | `cr_cfm` | bit | NO |
| 37 | `cr_cfm_by` | varchar(12) | NO |
| 38 | `cr_cfm_name` | varchar(30) | NO |
| 39 | `cr_cfm_date` | datetime | YES |
| 40 | `cr_sig` | bit | NO |
| 41 | `cr_sig_by` | varchar(12) | NO |
| 42 | `cr_sig_name` | varchar(30) | NO |
| 43 | `cr_sig_date` | datetime | YES |
| 44 | `cr_crt_name` | varchar(30) | NO |
| 45 | `cr_mod_name` | varchar(30) | NO |
| 46 | `cr_pst_name` | varchar(30) | NO |

### `dbo.crd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `crd_cr` | varchar(15) | NO |
| 2 | `crd_line` | int(10,0) | NO |
| 3 | `crd_so` | varchar(15) | NO |
| 4 | `crd_so_line` | int(10,0) | NO |
| 5 | `crd_part` | varchar(30) | NO |
| 6 | `crd_um` | varchar(4) | NO |
| 7 | `crd_um_rate_m` | decimal(19,8) | NO |
| 8 | `crd_um_rate_d` | decimal(19,8) | NO |
| 9 | `crd_qty_shp` | numeric(19,8) | NO |
| 10 | `crd_qty_spare_shp` | numeric(19,8) | NO |
| 11 | `crd_qty_rtn` | numeric(19,8) | NO |
| 12 | `crd_qty_spare_rtn` | numeric(19,8) | NO |
| 13 | `crd_loc` | varchar(8) | NO |
| 14 | `crd_lot` | varchar(18) | NO |
| 15 | `crd_price` | decimal(19,8) | NO |
| 16 | `crd_rmks` | varchar(255) | NO |
| 17 | `crd_crt_by` | varchar(12) | NO |
| 18 | `crd_crt_date` | datetime | NO |
| 19 | `crd_mod_times` | int(10,0) | NO |
| 20 | `crd_mod_by` | varchar(12) | NO |
| 21 | `crd_mod_date` | datetime | NO |
| 22 | `crd_char1` | varchar(255) | NO |
| 23 | `crd_char2` | varchar(255) | NO |
| 24 | `crd_char3` | varchar(255) | NO |
| 25 | `crd_char4` | varchar(255) | NO |
| 26 | `crd_char5` | varchar(255) | NO |
| 27 | `crd_char6` | varchar(255) | NO |
| 28 | `crd_qty1` | decimal(19,8) | NO |
| 29 | `crd_qty2` | decimal(19,8) | NO |
| 30 | `crd_cust_part` | varchar(80) | NO |
| 31 | `crd_data_src` | varchar(1) | NO |
| 32 | `crd_data_id` | varchar(255) | NO |
| 33 | `crd_crt_name` | varchar(30) | NO |
| 34 | `crd_mod_name` | varchar(30) | NO |

### `dbo.ct_part_stack` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ctst_part_sub` | varchar(30) | NO |
| 2 | `ctst_part` | varchar(30) | NO |

### `dbo.ct_pt_cost` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ct_site` | varchar(8) | NO |
| 2 | `ct_part` | varchar(30) | NO |
| 3 | `ct_loc_type` | varchar(30) | NO |
| 4 | `ct_cost_mtl` | decimal(19,8) | NO |
| 5 | `ct_cost_lbr` | decimal(19,8) | NO |
| 6 | `ct_cost_bdn` | decimal(19,8) | NO |
| 7 | `ct_cost_sub` | decimal(19,8) | NO |
| 8 | `ct_cost_mtlll` | decimal(19,8) | NO |
| 9 | `ct_cost_lbrll` | decimal(19,8) | NO |
| 10 | `ct_cost_bdnll` | decimal(19,8) | NO |
| 11 | `ct_cost_subll` | decimal(19,8) | NO |
| 12 | `ct_std_mtl` | decimal(19,8) | NO |
| 13 | `ct_std_lbr` | decimal(19,8) | NO |
| 14 | `ct_std_bdn` | decimal(19,8) | NO |
| 15 | `ct_std_sub` | decimal(19,8) | NO |
| 16 | `ct_std_mtlll` | decimal(19,8) | NO |
| 17 | `ct_std_lbrll` | decimal(19,8) | NO |
| 18 | `ct_std_bdnll` | decimal(19,8) | NO |
| 19 | `ct_std_subll` | decimal(19,8) | NO |
| 20 | `ct_flag` | int(10,0) | NO |
| 21 | `ct_lot` | varchar(18) | NO |

### `dbo.ct_step` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ct_year` | int(10,0) | NO |
| 2 | `ct_month` | int(10,0) | NO |
| 3 | `ct_site` | varchar(8) | NO |
| 4 | `ct_part` | varchar(30) | NO |
| 5 | `ct_level` | int(10,0) | NO |
| 6 | `ct_pt_ok` | bit | NO |
| 7 | `ct_need_times` | int(10,0) | NO |
| 8 | `ct_curr_times` | int(10,0) | NO |
| 9 | `ct_site_status` | varchar(2) | NO |
| 10 | `ct_start` | datetime | YES |
| 11 | `ct_end` | datetime | YES |

### `dbo.ct_tr_wadj` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tr_trnbr` | int(10,0) | NO |
| 2 | `tr_part` | varchar(30) | NO |
| 3 | `tr_type` | varchar(8) | NO |
| 4 | `tr_effdate` | datetime | NO |
| 5 | `tr_site` | varchar(8) | NO |
| 6 | `tr_loc` | varchar(8) | NO |
| 7 | `tr_qty_loc` | numeric(19,8) | NO |
| 8 | `tr_nbr` | varchar(15) | NO |
| 9 | `tr_line` | int(10,0) | NO |
| 10 | `tr_lot` | varchar(18) | NO |
| 11 | `tr_lotserial` | varchar(18) | NO |
| 12 | `tr_ord_rev` | varchar(4) | NO |
| 13 | `tr_mtl_tl` | decimal(19,8) | NO |
| 14 | `tr_mtl_ll` | decimal(19,8) | NO |
| 15 | `tr_lbr_tl` | decimal(19,8) | NO |
| 16 | `tr_lbr_ll` | decimal(19,8) | NO |
| 17 | `tr_bdn_tl` | decimal(19,8) | NO |
| 18 | `tr_bdn_ll` | decimal(19,8) | NO |
| 19 | `tr_sub_tl` | decimal(19,8) | NO |
| 20 | `tr_sub_ll` | decimal(19,8) | NO |
| 21 | `tr_cost_flag` | bit | NO |
| 22 | `tr_char1` | varchar(255) | NO |
| 23 | `tr_char2` | varchar(255) | NO |

### `dbo.ct_wo` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ctwo_year` | int(10,0) | NO |
| 2 | `ctwo_month` | int(10,0) | NO |
| 3 | `ctwo_wod_nbr` | varchar(15) | NO |
| 4 | `ctwo_wod_lot` | varchar(18) | NO |
| 5 | `ctwo_wod_part` | varchar(30) | NO |
| 6 | `ctwo_wod_flag` | bit | NO |
| 7 | `ctwo_flag` | int(10,0) | NO |

### `dbo.ct_wod_rts` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ct_year` | int(10,0) | NO |
| 2 | `ct_month` | int(10,0) | NO |
| 3 | `ct_wod_nbr` | varchar(15) | NO |
| 4 | `ct_wod_lot` | varchar(18) | NO |
| 5 | `ct_wod_seq` | int(10,0) | NO |
| 6 | `ct_wod_part` | varchar(30) | NO |
| 7 | `ct_beg_qty` | numeric(19,8) | NO |
| 8 | `ct_beg_mtl` | numeric(19,8) | NO |
| 9 | `ct_beg_lbr` | numeric(19,8) | NO |
| 10 | `ct_beg_bdn` | numeric(19,8) | NO |
| 11 | `ct_beg_sub` | numeric(19,8) | NO |
| 12 | `ct_beg_mtlll` | numeric(19,8) | NO |
| 13 | `ct_beg_lbrll` | numeric(19,8) | NO |
| 14 | `ct_beg_bdnll` | numeric(19,8) | NO |
| 15 | `ct_beg_subll` | numeric(19,8) | NO |
| 16 | `ct_iss_qty` | numeric(19,8) | NO |
| 17 | `ct_rtn_qty` | numeric(19,8) | NO |
| 18 | `ct_org_beg_qty` | numeric(19,8) | NO |
| 19 | `ct_org_beg_mtl` | numeric(19,8) | NO |
| 20 | `ct_org_beg_lbr` | numeric(19,8) | NO |
| 21 | `ct_org_beg_bdn` | numeric(19,8) | NO |
| 22 | `ct_org_beg_sub` | numeric(19,8) | NO |
| 23 | `ct_org_beg_mtlll` | numeric(19,8) | NO |
| 24 | `ct_org_beg_lbrll` | numeric(19,8) | NO |
| 25 | `ct_org_beg_bdnll` | numeric(19,8) | NO |
| 26 | `ct_org_beg_subll` | numeric(19,8) | NO |

### `dbo.cu_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cu_start` | datetime | NO |
| 2 | `cu_end` | datetime | NO |
| 3 | `cu_price` | decimal(19,8) | NO |
| 4 | `cu_curr` | varchar(4) | NO |
| 5 | `cu_rmks` | varchar(255) | NO |
| 6 | `cu_crt_by` | varchar(12) | NO |
| 7 | `cu_crt_date` | datetime | NO |
| 8 | `cu_mod_times` | int(10,0) | NO |
| 9 | `cu_mod_by` | varchar(12) | NO |
| 10 | `cu_mod_date` | datetime | NO |
| 11 | `cu_char1` | varchar(255) | NO |
| 12 | `cu_char2` | varchar(255) | NO |
| 13 | `cu_char3` | varchar(255) | NO |
| 14 | `cu_char4` | varchar(255) | NO |
| 15 | `cu_char5` | varchar(255) | NO |
| 16 | `cu_char6` | varchar(255) | NO |
| 17 | `cu_qty1` | decimal(19,8) | NO |
| 18 | `cu_qty2` | decimal(19,8) | NO |

### `dbo.dad_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dad_nbr` | varchar(15) | NO |
| 2 | `dad_line` | int(10,0) | NO |
| 3 | `dad_ac_code` | varchar(15) | NO |
| 4 | `dad_type` | int(10,0) | NO |
| 5 | `dad_aid_code` | varchar(30) | NO |
| 6 | `dad_content` | varchar(255) | NO |
| 7 | `dad_curr` | varchar(4) | NO |
| 8 | `dad_debit_amt` | numeric(19,8) | NO |
| 9 | `dad_credit_amt` | numeric(19,8) | NO |
| 10 | `dad_handler` | varchar(50) | NO |
| 11 | `dad_rmks` | varchar(255) | NO |
| 12 | `dad_crt_by` | varchar(12) | NO |
| 13 | `dad_crt_date` | datetime | NO |
| 14 | `dad_mod_times` | int(10,0) | NO |
| 15 | `dad_mod_by` | varchar(12) | NO |
| 16 | `dad_mod_date` | datetime | NO |
| 17 | `dad_char1` | varchar(255) | NO |
| 18 | `dad_char2` | varchar(255) | NO |
| 19 | `dad_char3` | varchar(255) | NO |
| 20 | `dad_char4` | varchar(255) | NO |
| 21 | `dad_char5` | varchar(255) | NO |
| 22 | `dad_char6` | varchar(255) | NO |
| 23 | `dad_qty1` | decimal(19,8) | NO |
| 24 | `dad_qty2` | decimal(19,8) | NO |

### `dbo.dn_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dn_dn` | varchar(15) | NO |
| 2 | `dn_date` | datetime | NO |
| 3 | `dn_cust` | varchar(8) | NO |
| 4 | `dn_loc` | varchar(8) | NO |
| 5 | `dn_rmks` | varchar(255) | NO |
| 6 | `dn_site` | varchar(8) | NO |
| 7 | `dn_prog_code` | varchar(12) | NO |
| 8 | `dn_doc_type` | varchar(12) | NO |
| 9 | `dn_wf_status` | varchar(1) | NO |
| 10 | `dn_crt_by` | varchar(12) | NO |
| 11 | `dn_crt_date` | datetime | NO |
| 12 | `dn_mod_times` | int(10,0) | NO |
| 13 | `dn_mod_by` | varchar(12) | NO |
| 14 | `dn_mod_date` | datetime | NO |
| 15 | `dn_pst` | bit | NO |
| 16 | `dn_pst_by` | varchar(12) | NO |
| 17 | `dn_pst_date` | datetime | YES |
| 18 | `dn_char1` | varchar(255) | NO |
| 19 | `dn_char2` | varchar(255) | NO |
| 20 | `dn_char3` | varchar(255) | NO |
| 21 | `dn_char4` | varchar(255) | NO |
| 22 | `dn_char5` | varchar(255) | NO |
| 23 | `dn_char6` | varchar(255) | NO |
| 24 | `dn_qty1` | decimal(19,8) | NO |
| 25 | `dn_qty2` | decimal(19,8) | NO |
| 26 | `dn_txt` | varchar(255) | NO |
| 27 | `dn_data_src` | varchar(1) | NO |
| 28 | `dn_data_id` | varchar(255) | NO |
| 29 | `dn_src` | varchar(2) | NO |
| 30 | `dn_src_nbr` | varchar(15) | NO |
| 31 | `dn_src_lot` | varchar(18) | NO |
| 32 | `dn_sig` | bit | NO |
| 33 | `dn_sig_by` | varchar(12) | NO |
| 34 | `dn_sig_date` | datetime | YES |
| 35 | `dn_cfm` | bit | NO |
| 36 | `dn_cfm_by` | varchar(12) | NO |
| 37 | `dn_cfm_date` | datetime | YES |

### `dbo.dna_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dna_nbr` | varchar(15) | NO |
| 2 | `dna_date` | datetime | NO |
| 3 | `dna_ship_date` | datetime | NO |
| 4 | `dna_cust` | varchar(8) | NO |
| 5 | `dna_rmks` | varchar(255) | NO |
| 6 | `dna_site` | varchar(8) | NO |
| 7 | `dna_prog_code` | varchar(12) | NO |
| 8 | `dna_doc_type` | varchar(12) | NO |
| 9 | `dna_wf_status` | varchar(1) | NO |
| 10 | `dna_crt_by` | varchar(12) | NO |
| 11 | `dna_crt_date` | datetime | NO |
| 12 | `dna_mod_times` | int(10,0) | NO |
| 13 | `dna_mod_by` | varchar(12) | NO |
| 14 | `dna_mod_date` | datetime | NO |
| 15 | `dna_pst` | bit | NO |
| 16 | `dna_pst_by` | varchar(12) | NO |
| 17 | `dna_pst_date` | datetime | YES |
| 18 | `dna_char1` | varchar(255) | NO |
| 19 | `dna_char2` | varchar(255) | NO |
| 20 | `dna_char3` | varchar(255) | NO |
| 21 | `dna_char4` | varchar(255) | NO |
| 22 | `dna_char5` | varchar(255) | NO |
| 23 | `dna_char6` | varchar(255) | NO |
| 24 | `dna_qty1` | decimal(19,8) | NO |
| 25 | `dna_qty2` | decimal(19,8) | NO |

### `dbo.dnad_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dnad_nbr` | varchar(15) | NO |
| 2 | `dnad_line` | int(10,0) | NO |
| 3 | `dnad_so` | varchar(15) | NO |
| 4 | `dnad_so_line` | int(10,0) | NO |
| 5 | `dnad_part` | varchar(30) | NO |
| 6 | `dnad_um` | varchar(4) | NO |
| 7 | `dnad_um_rate_m` | decimal(19,8) | NO |
| 8 | `dnad_um_rate_d` | decimal(19,8) | NO |
| 9 | `dnad_qty_ord` | numeric(19,8) | NO |
| 10 | `dnad_qty_spare` | numeric(19,8) | NO |
| 11 | `dnad_qty_ship` | numeric(19,8) | NO |
| 12 | `dnad_qty_spare_ship` | numeric(19,8) | NO |
| 13 | `dnad_qty_shipped` | numeric(19,8) | NO |
| 14 | `dnad_qty_spared` | numeric(19,8) | NO |
| 15 | `dnad_rmks` | varchar(255) | NO |
| 16 | `dnad_close` | bit | NO |
| 17 | `dnad_close_by` | varchar(12) | NO |
| 18 | `dnad_close_date` | datetime | YES |
| 19 | `dnad_crt_by` | varchar(12) | NO |
| 20 | `dnad_crt_date` | datetime | NO |
| 21 | `dnad_mod_times` | int(10,0) | NO |
| 22 | `dnad_mod_by` | varchar(12) | NO |
| 23 | `dnad_mod_date` | datetime | NO |
| 24 | `dnad_char1` | varchar(255) | NO |
| 25 | `dnad_char2` | varchar(255) | NO |
| 26 | `dnad_char3` | varchar(255) | NO |
| 27 | `dnad_char4` | varchar(255) | NO |
| 28 | `dnad_char5` | varchar(255) | NO |
| 29 | `dnad_char6` | varchar(255) | NO |
| 30 | `dnad_qty1` | decimal(19,8) | NO |
| 31 | `dnad_qty2` | decimal(19,8) | NO |

### `dbo.dnd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dnd_dn` | varchar(15) | NO |
| 2 | `dnd_line` | int(10,0) | NO |
| 3 | `dnd_dna` | varchar(15) | NO |
| 4 | `dnd_dna_line` | int(10,0) | NO |
| 5 | `dnd_so` | varchar(15) | NO |
| 6 | `dnd_so_line` | int(10,0) | NO |
| 7 | `dnd_part` | varchar(30) | NO |
| 8 | `dnd_um` | varchar(4) | NO |
| 9 | `dnd_um_rate_m` | decimal(19,8) | NO |
| 10 | `dnd_um_rate_d` | decimal(19,8) | NO |
| 11 | `dnd_loc` | varchar(8) | NO |
| 12 | `dnd_lot` | varchar(18) | NO |
| 13 | `dnd_qty_ord` | numeric(19,8) | NO |
| 14 | `dnd_qty_spare` | numeric(19,8) | NO |
| 15 | `dnd_qty_shipped` | numeric(19,8) | NO |
| 16 | `dnd_qty_spared` | numeric(19,8) | NO |
| 17 | `dnd_qty_ship` | numeric(19,8) | NO |
| 18 | `dnd_qty_spare_ship` | numeric(19,8) | NO |
| 19 | `dnd_rmks` | varchar(255) | NO |
| 20 | `dnd_crt_by` | varchar(12) | NO |
| 21 | `dnd_crt_date` | datetime | NO |
| 22 | `dnd_mod_times` | int(10,0) | NO |
| 23 | `dnd_mod_by` | varchar(12) | NO |
| 24 | `dnd_mod_date` | datetime | NO |
| 25 | `dnd_char1` | varchar(255) | NO |
| 26 | `dnd_char2` | varchar(255) | NO |
| 27 | `dnd_char3` | varchar(255) | NO |
| 28 | `dnd_char4` | varchar(255) | NO |
| 29 | `dnd_char5` | varchar(255) | NO |
| 30 | `dnd_char6` | varchar(255) | NO |
| 31 | `dnd_qty1` | decimal(19,8) | NO |
| 32 | `dnd_qty2` | decimal(19,8) | NO |
| 33 | `dnd_data_src` | varchar(1) | NO |
| 34 | `dnd_data_id` | varchar(255) | NO |

### `dbo.dp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dp_code` | varchar(10) | NO |
| 2 | `dp_name` | varchar(50) | NO |
| 3 | `dp_manager` | varchar(30) | NO |
| 4 | `dp_rmks` | varchar(255) | NO |
| 5 | `dp_upper_dept` | varchar(10) | NO |
| 6 | `dp_crt_by` | varchar(12) | NO |
| 7 | `dp_crt_date` | datetime | NO |
| 8 | `dp_char1` | varchar(255) | NO |
| 9 | `dp_char2` | varchar(255) | NO |
| 10 | `dp_char3` | varchar(255) | NO |
| 11 | `dp_char4` | varchar(255) | NO |
| 12 | `dp_char5` | varchar(255) | NO |
| 13 | `dp_char6` | varchar(255) | NO |
| 14 | `dp_qty1` | decimal(19,8) | NO |
| 15 | `dp_qty2` | decimal(19,8) | NO |

### `dbo.dpm_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dpm_nbr` | varchar(15) | NO |
| 2 | `dpm_date` | datetime | NO |
| 3 | `dpm_wkctr` | varchar(8) | NO |
| 4 | `dpm_emp` | varchar(12) | NO |
| 5 | `dpm_rmks` | varchar(255) | NO |
| 6 | `dpm_site` | varchar(8) | NO |
| 7 | `dpm_wf_status` | varchar(1) | NO |
| 8 | `dpm_prog_code` | varchar(12) | NO |
| 9 | `dpm_doc_code` | varchar(12) | NO |
| 10 | `dpm_crt_by` | varchar(12) | NO |
| 11 | `dpm_crt_date` | datetime | NO |
| 12 | `dpm_mod_times` | int(10,0) | NO |
| 13 | `dpm_mod_by` | varchar(12) | NO |
| 14 | `dpm_mod_date` | datetime | NO |
| 15 | `dpm_pst` | bit | NO |
| 16 | `dpm_pst_by` | varchar(12) | NO |
| 17 | `dpm_pst_date` | datetime | YES |
| 18 | `dpm_char1` | varchar(255) | NO |
| 19 | `dpm_char2` | varchar(255) | NO |
| 20 | `dpm_char3` | varchar(255) | NO |
| 21 | `dpm_char4` | varchar(255) | NO |
| 22 | `dpm_char5` | varchar(255) | NO |
| 23 | `dpm_char6` | varchar(255) | NO |
| 24 | `dpm_qty1` | decimal(19,8) | NO |
| 25 | `dpm_qty2` | decimal(19,8) | NO |
| 26 | `dpm_data_src` | varchar(1) | NO |
| 27 | `dpm_data_id` | varchar(255) | NO |

### `dbo.dpmd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dpmd_nbr` | varchar(15) | NO |
| 2 | `dpmd_line` | int(10,0) | NO |
| 3 | `dpmd_date` | datetime | NO |
| 4 | `dpmd_wr_nbr` | varchar(15) | NO |
| 5 | `dpmd_wr_lot` | varchar(18) | NO |
| 6 | `dpmd_wr_op` | int(10,0) | NO |
| 7 | `dpmd_wr_desc` | varchar(100) | NO |
| 8 | `dpmd_part` | varchar(30) | NO |
| 9 | `dpmd_emp` | varchar(12) | NO |
| 10 | `dpmd_start` | varchar(10) | NO |
| 11 | `dpmd_end` | varchar(10) | NO |
| 12 | `dpmd_qty_ord` | numeric(19,8) | NO |
| 13 | `dpmd_qty_rework` | numeric(19,8) | NO |
| 14 | `dpmd_qty_comp` | numeric(19,8) | NO |
| 15 | `dpmd_qty_rjct` | numeric(19,8) | NO |
| 16 | `dpmd_rmks` | varchar(255) | NO |
| 17 | `dpmd_status` | varchar(1) | NO |
| 18 | `dpmd_close_by` | varchar(12) | NO |
| 19 | `dpmd_close_date` | datetime | YES |
| 20 | `dpmd_crt_by` | varchar(12) | NO |
| 21 | `dpmd_crt_date` | datetime | NO |
| 22 | `dpmd_mod_times` | int(10,0) | NO |
| 23 | `dpmd_mod_by` | varchar(12) | NO |
| 24 | `dpmd_mod_date` | datetime | NO |
| 25 | `dpmd_char1` | varchar(255) | NO |
| 26 | `dpmd_char2` | varchar(255) | NO |
| 27 | `dpmd_char3` | varchar(255) | NO |
| 28 | `dpmd_char4` | varchar(255) | NO |
| 29 | `dpmd_char5` | varchar(255) | NO |
| 30 | `dpmd_char6` | varchar(255) | NO |
| 31 | `dpmd_qty1` | decimal(19,8) | NO |
| 32 | `dpmd_qty2` | decimal(19,8) | NO |

### `dbo.ecd1_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ecd1_nbr` | varchar(15) | NO |
| 2 | `ecd1_line` | int(10,0) | NO |
| 3 | `ecd1_type` | varchar(1) | NO |
| 4 | `ecd1_category` | varchar(1) | NO |
| 5 | `ecd1_par` | varchar(30) | NO |
| 6 | `ecd1_version_old` | varchar(15) | NO |
| 7 | `ecd1_version_new` | varchar(15) | NO |
| 8 | `ecd1_comp` | varchar(30) | NO |
| 9 | `ecd1_start` | datetime | YES |
| 10 | `ecd1_comp_old` | varchar(30) | NO |
| 11 | `ecd1_qty_m_old` | decimal(19,8) | NO |
| 12 | `ecd1_qty_d_old` | decimal(19,8) | NO |
| 13 | `ecd1_op_old` | int(10,0) | NO |
| 14 | `ecd1_scrp_pct_old` | decimal(19,8) | NO |
| 15 | `ecd1_lt_off_old` | int(10,0) | NO |
| 16 | `ecd1_seq_old` | int(10,0) | NO |
| 17 | `ecd1_rmks_old` | varchar(255) | NO |
| 18 | `ecd1_char1_old` | varchar(255) | NO |
| 19 | `ecd1_char2_old` | varchar(255) | NO |
| 20 | `ecd1_char3_old` | varchar(255) | NO |
| 21 | `ecd1_char4_old` | varchar(255) | NO |
| 22 | `ecd1_char5_old` | varchar(255) | NO |
| 23 | `ecd1_char6_old` | varchar(255) | NO |
| 24 | `ecd1_qty1_old` | decimal(19,8) | NO |
| 25 | `ecd1_qty2_old` | decimal(19,8) | NO |
| 26 | `ecd1_comp_new` | varchar(30) | NO |
| 27 | `ecd1_qty_m_new` | decimal(19,8) | NO |
| 28 | `ecd1_qty_d_new` | decimal(19,8) | NO |
| 29 | `ecd1_op_new` | int(10,0) | NO |
| 30 | `ecd1_scrp_pct_new` | decimal(19,8) | NO |
| 31 | `ecd1_lt_off_new` | int(10,0) | NO |
| 32 | `ecd1_seq_new` | int(10,0) | NO |
| 33 | `ecd1_rmks_new` | varchar(255) | NO |
| 34 | `ecd1_char1_new` | varchar(255) | NO |
| 35 | `ecd1_char2_new` | varchar(255) | NO |
| 36 | `ecd1_char3_new` | varchar(255) | NO |
| 37 | `ecd1_char4_new` | varchar(255) | NO |
| 38 | `ecd1_char5_new` | varchar(255) | NO |
| 39 | `ecd1_char6_new` | varchar(255) | NO |
| 40 | `ecd1_qty1_new` | decimal(19,8) | NO |
| 41 | `ecd1_qty2_new` | decimal(19,8) | NO |
| 42 | `ecd1_rmks` | varchar(255) | NO |
| 43 | `ecd1_crt_by` | varchar(12) | NO |
| 44 | `ecd1_crt_date` | datetime | NO |
| 45 | `ecd1_mod_times` | int(10,0) | NO |
| 46 | `ecd1_mod_by` | varchar(12) | NO |
| 47 | `ecd1_mod_date` | datetime | NO |
| 48 | `ecd1_char1` | varchar(255) | NO |
| 49 | `ecd1_char2` | varchar(255) | NO |
| 50 | `ecd1_char3` | varchar(255) | NO |
| 51 | `ecd1_char4` | varchar(255) | NO |
| 52 | `ecd1_char5` | varchar(255) | NO |
| 53 | `ecd1_char6` | varchar(255) | NO |
| 54 | `ecd1_qty1` | decimal(19,8) | NO |
| 55 | `ecd1_qty2` | decimal(19,8) | NO |
| 56 | `ecd1_exchange` | bit | NO |
| 57 | `ecd1_pts_type` | varchar(1) | NO |
| 58 | `ecd1_pts_old` | varchar(30) | NO |
| 59 | `ecd1_pts_new` | varchar(30) | YES |
| 60 | `ecd1_pts_qty_m` | numeric(19,8) | NO |
| 61 | `ecd1_pts_qty_d` | numeric(19,8) | NO |

### `dbo.ecd3_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ecd3_nbr` | varchar(15) | NO |
| 2 | `ecd3_line` | int(10,0) | NO |
| 3 | `ecd3_type` | varchar(1) | NO |
| 4 | `ecd3_sub_part` | varchar(30) | NO |
| 5 | `ecd3_start` | datetime | NO |
| 6 | `ecd3_end` | datetime | NO |
| 7 | `ecd3_qty_m` | numeric(19,8) | NO |
| 8 | `ecd3_qty_d` | numeric(19,8) | NO |
| 9 | `ecd3_priority` | int(10,0) | NO |
| 10 | `ecd3_rmks` | varchar(255) | NO |
| 11 | `ecd3_crt_by` | varchar(12) | NO |
| 12 | `ecd3_crt_date` | datetime | NO |
| 13 | `ecd3_mod_times` | int(10,0) | NO |
| 14 | `ecd3_mod_by` | varchar(12) | NO |
| 15 | `ecd3_mod_date` | datetime | NO |
| 16 | `ecd3_char1` | varchar(255) | NO |
| 17 | `ecd3_char2` | varchar(255) | NO |
| 18 | `ecd3_char3` | varchar(255) | NO |
| 19 | `ecd3_char4` | varchar(255) | NO |
| 20 | `ecd3_char5` | varchar(255) | NO |
| 21 | `ecd3_char6` | varchar(255) | NO |
| 22 | `ecd3_qty1` | decimal(19,8) | NO |
| 23 | `ecd3_qty2` | decimal(19,8) | NO |

### `dbo.en_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `en_company` | varchar(8) | NO |
| 2 | `en_cname` | varchar(50) | NO |
| 3 | `en_ename` | varchar(255) | NO |
| 4 | `en_curr` | varchar(4) | NO |
| 5 | `en_start` | datetime | NO |
| 6 | `en_crt_by` | varchar(12) | NO |
| 7 | `en_crt_date` | datetime | NO |
| 8 | `en_char1` | varchar(255) | NO |
| 9 | `en_char2` | varchar(255) | NO |
| 10 | `en_char3` | varchar(255) | NO |
| 11 | `en_char4` | varchar(255) | NO |
| 12 | `en_char5` | varchar(255) | NO |
| 13 | `en_char6` | varchar(255) | NO |
| 14 | `en_qty1` | decimal(19,8) | NO |
| 15 | `en_qty2` | decimal(19,8) | NO |
| 16 | `en_org_code` | varchar(50) | NO |
| 17 | `en_nature` | varchar(50) | NO |
| 18 | `en_industry` | varchar(50) | NO |

### `dbo.ex_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ex_curr` | varchar(4) | NO |
| 2 | `ex_desc` | varchar(30) | NO |
| 3 | `ex_symbol` | varchar(10) | NO |
| 4 | `ex_crt_by` | varchar(12) | NO |
| 5 | `ex_crt_date` | datetime | NO |
| 6 | `ex_char1` | varchar(255) | NO |
| 7 | `ex_char2` | varchar(255) | NO |
| 8 | `ex_char3` | varchar(255) | NO |
| 9 | `ex_char4` | varchar(255) | NO |
| 10 | `ex_char5` | varchar(255) | NO |
| 11 | `ex_char6` | varchar(255) | NO |
| 12 | `ex_qty1` | decimal(19,8) | NO |
| 13 | `ex_qty2` | decimal(19,8) | NO |

### `dbo.exd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `exd_curr` | varchar(4) | NO |
| 2 | `exd_eff_date` | datetime | NO |
| 3 | `exd_end_date` | datetime | NO |
| 4 | `exd_rate` | decimal(19,8) | NO |
| 5 | `exd_crt_by` | varchar(12) | NO |
| 6 | `exd_crt_date` | datetime | NO |
| 7 | `exd_mod_times` | int(10,0) | NO |
| 8 | `exd_mod_by` | varchar(12) | NO |
| 9 | `exd_mod_date` | datetime | NO |
| 10 | `exd_char1` | varchar(255) | NO |
| 11 | `exd_char2` | varchar(255) | NO |
| 12 | `exd_char3` | varchar(255) | NO |
| 13 | `exd_char4` | varchar(255) | NO |
| 14 | `exd_char5` | varchar(255) | NO |
| 15 | `exd_char6` | varchar(255) | NO |
| 16 | `exd_qty1` | decimal(19,8) | NO |
| 17 | `exd_qty2` | decimal(19,8) | NO |
| 18 | `exd_end_rate` | decimal(19,8) | NO |

### `dbo.exp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `exp_prog` | varchar(12) | NO |
| 2 | `exp_seq` | int(10,0) | NO |
| 3 | `exp_sheet_idx` | int(10,0) | NO |
| 4 | `exp_title` | varchar(255) | NO |
| 5 | `exp_row` | int(10,0) | NO |
| 6 | `exp_col` | int(10,0) | NO |
| 7 | `exp_new_row` | bit | NO |
| 8 | `exp_detail` | bit | NO |
| 9 | `exp_merge` | varchar(30) | NO |
| 10 | `exp_fld_name` | varchar(30) | NO |
| 11 | `exp_fld_curr` | varchar(30) | NO |
| 12 | `exp_format` | varchar(255) | NO |
| 13 | `exp_crt_by` | varchar(12) | NO |
| 14 | `exp_crt_date` | datetime | NO |
| 15 | `exp_mod_times` | int(10,0) | NO |
| 16 | `exp_mod_by` | varchar(12) | NO |
| 17 | `exp_mod_date` | datetime | NO |
| 18 | `exp_char1` | varchar(255) | NO |
| 19 | `exp_char2` | varchar(255) | NO |
| 20 | `exp_char3` | varchar(255) | NO |
| 21 | `exp_char4` | varchar(255) | NO |
| 22 | `exp_char5` | varchar(255) | NO |
| 23 | `exp_char6` | varchar(255) | NO |
| 24 | `exp_qty1` | decimal(19,8) | NO |
| 25 | `exp_qty2` | decimal(19,8) | NO |
| 26 | `exp_procedure_name` | varchar(50) | NO |
| 27 | `exp_prefix` | varchar(255) | NO |
| 28 | `exp_suffix` | varchar(255) | NO |

### `dbo.export_CTEXMTA1` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ctex_prod_flow` | int(10,0) | NO |
| 2 | `ctex_prod_no` | varchar(30) | NO |
| 3 | `ctex_prod_name` | varchar(255) | NO |
| 4 | `ctex_prod_spec` | varchar(255) | NO |
| 5 | `ctex_prod_um` | varchar(4) | NO |
| 6 | `ctex_prod_vend` | varchar(8) | NO |
| 7 | `ctex_prod_vd_sort` | varchar(255) | NO |
| 8 | `ctex_prod_pc_vat` | numeric(19,8) | NO |
| 9 | `ctex_prod_mtl_cost` | numeric(19,8) | NO |
| 10 | `ctex_prod_lbr_cost` | numeric(19,8) | NO |
| 11 | `ctex_prod_bdn_cost` | numeric(19,8) | NO |
| 12 | `ctex_prod_sub_cost` | numeric(19,8) | NO |
| 13 | `ctex_prod_tot_cost` | numeric(19,8) | NO |
| 14 | `ctex_prod_std_cost` | numeric(19,8) | NO |
| 15 | `ctex_tmp1_level` | varchar(30) | NO |
| 16 | `ctex_tmp1_comp` | varchar(30) | NO |
| 17 | `ctex_tmp1_qty_per_m` | numeric(19,8) | NO |
| 18 | `ctex_tmp1_qty_per_d` | numeric(19,8) | NO |
| 19 | `ctex_tmp1_um` | varchar(4) | NO |
| 20 | `ctex_tmp1_desc` | varchar(255) | NO |
| 21 | `ctex_tmp1_spec` | varchar(255) | NO |
| 22 | `ctex_tmp1_unit_cost` | numeric(19,8) | NO |
| 23 | `ctex_tmp1_mtl_cost` | numeric(19,8) | NO |
| 24 | `ctex_tmp1_lbr_cost` | numeric(19,8) | NO |
| 25 | `ctex_tmp1_bdn_cost` | numeric(19,8) | NO |
| 26 | `ctex_tmp1_sub_cost` | numeric(19,8) | NO |
| 27 | `ctex_tmp1_tot_cost` | numeric(19,8) | NO |
| 28 | `ctex_tmp1_par_flag` | bit | NO |
| 29 | `ctex_tmp1_vendor` | varchar(8) | NO |
| 30 | `ctex_tmp1_vd_sort` | varchar(255) | NO |
| 31 | `ctex_tmp1_pc_vat` | numeric(19,8) | NO |
| 32 | `ctex_tmp1_pc_curr` | varchar(4) | NO |
| 33 | `ctex_tmp1_pc_price` | numeric(19,8) | NO |
| 34 | `ctex_tmp1_pc_nbr` | varchar(15) | NO |
| 35 | `ctex_tmp1_alt_flow` | int(10,0) | NO |
| 36 | `ctex_tmp1_has_alt` | bit | NO |
| 37 | `ctex_tmp1_flag` | bit | NO |
| 38 | `ctex_ptp3_mtl_stdtl` | numeric(19,8) | NO |
| 39 | `ctex_ptp3_lbr_stdtl` | numeric(19,8) | NO |
| 40 | `ctex_ptp3_bdn_stdtl` | numeric(19,8) | NO |
| 41 | `ctex_ptp3_sub_stdtl` | numeric(19,8) | NO |
| 42 | `ctex_ptp3_mtl_stdll` | numeric(19,8) | NO |
| 43 | `ctex_ptp3_lbr_stdll` | numeric(19,8) | NO |
| 44 | `ctex_ptp3_bdn_stdll` | numeric(19,8) | NO |
| 45 | `ctex_ptp3_sub_stdll` | numeric(19,8) | NO |

### `dbo.extp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `extp_code` | varchar(12) | NO |
| 2 | `extp_name` | varchar(255) | NO |
| 3 | `extp_prog` | varchar(12) | NO |
| 4 | `extp_path` | varchar(255) | NO |
| 5 | `extp_perms` | varchar(255) | NO |
| 6 | `extp_type` | varchar(1) | NO |
| 7 | `extp_det_proc` | varchar(80) | NO |
| 8 | `extp_rmks` | varchar(255) | NO |
| 9 | `extp_crt_by` | varchar(12) | NO |
| 10 | `extp_crt_date` | datetime | NO |
| 11 | `extp_mod_times` | int(10,0) | NO |
| 12 | `extp_mod_by` | varchar(12) | NO |
| 13 | `extp_mod_date` | datetime | NO |
| 14 | `extp_pst` | bit | NO |
| 15 | `extp_pst_by` | varchar(12) | NO |
| 16 | `extp_pst_date` | datetime | YES |
| 17 | `extp_char1` | varchar(255) | NO |
| 18 | `extp_char2` | varchar(255) | NO |
| 19 | `extp_char3` | varchar(255) | NO |
| 20 | `extp_char4` | varchar(255) | NO |
| 21 | `extp_char5` | varchar(255) | NO |
| 22 | `extp_char6` | varchar(255) | NO |
| 23 | `extp_qty1` | decimal(19,8) | NO |
| 24 | `extp_qty2` | decimal(19,8) | NO |

### `dbo.fa_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fa_table` | varchar(50) | NO |
| 2 | `fa_field` | varchar(50) | NO |
| 3 | `fa_prog_code` | varchar(12) | NO |
| 4 | `fa_doc_code` | varchar(12) | NO |
| 5 | `fa_caption` | varchar(50) | NO |
| 6 | `fa_view_perm` | varchar(80) | NO |
| 7 | `fa_edit_perm` | varchar(80) | NO |
| 8 | `fa_crt_by` | varchar(12) | NO |
| 9 | `fa_crt_date` | datetime | NO |
| 10 | `fa_mod_times` | int(10,0) | NO |
| 11 | `fa_mod_by` | varchar(12) | NO |
| 12 | `fa_mod_date` | datetime | NO |
| 13 | `fa_char1` | varchar(255) | NO |
| 14 | `fa_char2` | varchar(255) | NO |
| 15 | `fa_char3` | varchar(255) | NO |
| 16 | `fa_char4` | varchar(255) | NO |
| 17 | `fa_char5` | varchar(255) | NO |
| 18 | `fa_char6` | varchar(255) | NO |
| 19 | `fa_qty1` | decimal(19,8) | NO |
| 20 | `fa_qty2` | decimal(19,8) | NO |

### `dbo.fac_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fac_fac` | int(10,0) | NO |
| 2 | `fac_old_dept` | bit | NO |
| 3 | `fac_dpc_new` | bit | NO |
| 4 | `fac_dpc_chg` | bit | NO |
| 5 | `fac_dpc_end` | varchar(1) | NO |
| 6 | `fac_to_vo_date` | datetime | NO |
| 7 | `fac_new_gl` | varchar(1) | NO |
| 8 | `fac_dpc_gl` | varchar(1) | NO |
| 9 | `fac_chg_gl` | varchar(1) | NO |
| 10 | `fac_new_doc` | varchar(15) | NO |
| 11 | `fac_dpc_doc` | varchar(15) | NO |
| 12 | `fac_chg_doc` | varchar(15) | NO |
| 13 | `fac_new_gl_code` | varchar(1) | NO |
| 14 | `fac_dpc_gl_code` | varchar(1) | NO |
| 15 | `fac_chg_gl_code` | varchar(1) | NO |
| 16 | `fac_crt_by` | varchar(12) | NO |
| 17 | `fac_crt_date` | datetime | NO |
| 18 | `fac_mod_times` | int(10,0) | NO |
| 19 | `fac_mod_by` | varchar(12) | NO |
| 20 | `fac_mod_date` | datetime | NO |
| 21 | `fac_char1` | varchar(255) | NO |
| 22 | `fac_char2` | varchar(255) | NO |
| 23 | `fac_char3` | varchar(255) | NO |
| 24 | `fac_char4` | varchar(255) | NO |
| 25 | `fac_char5` | varchar(255) | NO |
| 26 | `fac_char6` | varchar(255) | NO |
| 27 | `fac_qty1` | decimal(19,8) | NO |
| 28 | `fac_qty2` | decimal(19,8) | NO |
| 29 | `fac_to_vo_type` | varchar(1) | NO |
| 30 | `fac_ac_curr` | varchar(15) | NO |
| 31 | `fac_ac_vat` | varchar(15) | NO |
| 32 | `fac_ac_vat_sales` | varchar(15) | NO |
| 33 | `fac_ac_liquidation` | varchar(15) | NO |
| 34 | `fac_ac_ar` | varchar(15) | NO |
| 35 | `fac_ac_income` | varchar(15) | NO |
| 36 | `fac_ac_expenses` | varchar(15) | NO |
| 37 | `fac_far_part` | varchar(30) | NO |

### `dbo.far_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `far_company` | varchar(8) | NO |
| 2 | `far_nbr` | varchar(15) | NO |
| 3 | `far_rcv_date` | datetime | NO |
| 4 | `far_fac_nbr` | varchar(15) | NO |
| 5 | `far_fac_line` | int(10,0) | NO |
| 6 | `far_fas_code` | varchar(15) | NO |
| 7 | `far_qty` | numeric(19,8) | NO |
| 8 | `far_abn_type` | varchar(30) | NO |
| 9 | `far_abn_desc` | varchar(255) | NO |
| 10 | `far_rpd_date` | datetime | YES |
| 11 | `far_prop` | varchar(30) | NO |
| 12 | `far_prop_desc` | varchar(255) | NO |
| 13 | `far_rmks` | varchar(255) | NO |
| 14 | `far_prog_code` | varchar(12) | NO |
| 15 | `far_wf_status` | varchar(1) | NO |
| 16 | `far_crt_by` | varchar(12) | NO |
| 17 | `far_crt_date` | datetime | NO |
| 18 | `far_mod_times` | int(10,0) | NO |
| 19 | `far_mod_by` | varchar(12) | NO |
| 20 | `far_mod_date` | datetime | NO |
| 21 | `far_pst` | bit | NO |
| 22 | `far_pst_by` | varchar(12) | NO |
| 23 | `far_pst_date` | datetime | YES |
| 24 | `far_chk` | bit | NO |
| 25 | `far_chk_by` | varchar(12) | NO |
| 26 | `far_chk_date` | datetime | YES |
| 27 | `far_char1` | varchar(255) | NO |
| 28 | `far_char2` | varchar(255) | NO |
| 29 | `far_char3` | varchar(255) | NO |
| 30 | `far_char4` | varchar(255) | NO |
| 31 | `far_char5` | varchar(255) | NO |
| 32 | `far_char6` | varchar(255) | NO |
| 33 | `far_qty1` | decimal(19,8) | NO |
| 34 | `far_qty2` | decimal(19,8) | NO |
| 35 | `far_req_date` | datetime | YES |
| 36 | `far_prom_date` | datetime | YES |
| 37 | `far_vend` | varchar(8) | NO |
| 38 | `far_curr` | varchar(4) | NO |
| 39 | `far_vat` | numeric(19,8) | NO |
| 40 | `far_part` | varchar(30) | NO |
| 41 | `far_pt_desc` | varchar(255) | NO |
| 42 | `far_amt` | numeric(19,8) | NO |

### `dbo.fas_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fas_company` | varchar(8) | NO |
| 2 | `fas_code` | varchar(15) | NO |
| 3 | `fas_name` | varchar(255) | NO |
| 4 | `fas_card_no` | varchar(80) | NO |
| 5 | `fas_spec` | varchar(255) | NO |
| 6 | `fas_type` | varchar(15) | NO |
| 7 | `fas_status` | varchar(1) | NO |
| 8 | `fas_dept` | varchar(10) | NO |
| 9 | `fas_keeper` | varchar(12) | NO |
| 10 | `fas_place` | varchar(30) | NO |
| 11 | `fas_vendor` | varchar(8) | NO |
| 12 | `fas_manufct` | varchar(50) | NO |
| 13 | `fas_rmks` | varchar(255) | NO |
| 14 | `fas_qty` | numeric(19,8) | NO |
| 15 | `fas_um` | varchar(4) | NO |
| 16 | `fas_src` | varchar(10) | NO |
| 17 | `fas_get_date` | datetime | NO |
| 18 | `fas_check_mth` | int(10,0) | NO |
| 19 | `fas_curr` | varchar(4) | NO |
| 20 | `fas_ex_rate` | decimal(19,8) | NO |
| 21 | `fas_amt` | numeric(19,8) | NO |
| 22 | `fas_amt_base` | numeric(19,8) | NO |
| 23 | `fas_amt_imprv` | numeric(19,8) | NO |
| 24 | `fas_life_mth` | int(10,0) | NO |
| 25 | `fas_used_mth` | int(10,0) | NO |
| 26 | `fas_work_qty` | numeric(19,8) | NO |
| 27 | `fas_used_qty` | numeric(19,8) | NO |
| 28 | `fas_dpc` | bit | NO |
| 29 | `fas_dpc_method` | varchar(1) | NO |
| 30 | `fas_net_rate` | decimal(19,8) | NO |
| 31 | `fas_net_value` | numeric(19,8) | NO |
| 32 | `fas_tot_dpc_amt` | numeric(19,8) | NO |
| 33 | `fas_amt_impm` | numeric(19,8) | NO |
| 34 | `fas_ac_code1` | varchar(15) | NO |
| 35 | `fas_ac_code2` | varchar(15) | NO |
| 36 | `fas_ac_code3` | varchar(15) | NO |
| 37 | `fas_ac_code4` | varchar(15) | NO |
| 38 | `fas_crt_by` | varchar(12) | NO |
| 39 | `fas_crt_date` | datetime | NO |
| 40 | `fas_mod_times` | int(10,0) | NO |
| 41 | `fas_mod_by` | varchar(12) | NO |
| 42 | `fas_mod_date` | datetime | NO |
| 43 | `fas_pst` | bit | NO |
| 44 | `fas_pst_by` | varchar(12) | NO |
| 45 | `fas_pst_date` | datetime | YES |
| 46 | `fas_cancel` | bit | NO |
| 47 | `fas_canc_date` | datetime | YES |
| 48 | `fas_cancel_by` | varchar(12) | NO |
| 49 | `fas_cancel_date` | datetime | YES |
| 50 | `fas_char1` | varchar(255) | NO |
| 51 | `fas_char2` | varchar(255) | NO |
| 52 | `fas_char3` | varchar(255) | NO |
| 53 | `fas_char4` | varchar(255) | NO |
| 54 | `fas_char5` | varchar(255) | NO |
| 55 | `fas_char6` | varchar(255) | NO |
| 56 | `fas_qty1` | decimal(19,8) | NO |
| 57 | `fas_qty2` | decimal(19,8) | NO |
| 58 | `fas_vo_nbr` | varchar(15) | NO |
| 59 | `fas_vat` | decimal(19,8) | NO |
| 60 | `fas_vat_amt` | numeric(19,8) | NO |
| 61 | `fas_vat_base` | numeric(19,8) | NO |

### `dbo.fasd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fasd_code` | varchar(15) | NO |
| 2 | `fasd_mch` | varchar(10) | NO |
| 3 | `fasd_name` | varchar(255) | NO |
| 4 | `fasd_place` | varchar(30) | NO |
| 5 | `fasd_qty` | numeric(19,8) | NO |
| 6 | `fasd_rmks` | varchar(255) | NO |
| 7 | `fasd_crt_by` | varchar(12) | NO |
| 8 | `fasd_crt_date` | datetime | NO |
| 9 | `fasd_mod_times` | int(10,0) | NO |
| 10 | `fasd_mod_by` | varchar(12) | NO |
| 11 | `fasd_mod_date` | datetime | NO |
| 12 | `fasd_char1` | varchar(255) | NO |
| 13 | `fasd_char2` | varchar(255) | NO |
| 14 | `fasd_char3` | varchar(255) | NO |
| 15 | `fasd_char4` | varchar(255) | NO |
| 16 | `fasd_char5` | varchar(255) | NO |
| 17 | `fasd_char6` | varchar(255) | NO |
| 18 | `fasd_qty1` | decimal(19,8) | NO |
| 19 | `fasd_qty2` | decimal(19,8) | NO |

### `dbo.fc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fc_nbr` | varchar(15) | NO |
| 2 | `fc_date` | datetime | NO |
| 3 | `fc_cust` | varchar(8) | NO |
| 4 | `fc_mrp` | bit | NO |
| 5 | `fc_rmks` | varchar(255) | NO |
| 6 | `fc_site` | varchar(8) | NO |
| 7 | `fc_wf_status` | varchar(1) | NO |
| 8 | `fc_prog_code` | varchar(12) | NO |
| 9 | `fc_doc_code` | varchar(12) | NO |
| 10 | `fc_crt_by` | varchar(12) | NO |
| 11 | `fc_crt_date` | datetime | NO |
| 12 | `fc_mod_times` | int(10,0) | NO |
| 13 | `fc_mod_by` | varchar(12) | NO |
| 14 | `fc_mod_date` | datetime | NO |
| 15 | `fc_pst` | bit | NO |
| 16 | `fc_pst_by` | varchar(12) | NO |
| 17 | `fc_pst_date` | datetime | YES |
| 18 | `fc_char1` | varchar(255) | NO |
| 19 | `fc_char2` | varchar(255) | NO |
| 20 | `fc_char3` | varchar(255) | NO |
| 21 | `fc_char4` | varchar(255) | NO |
| 22 | `fc_char5` | varchar(255) | NO |
| 23 | `fc_char6` | varchar(255) | NO |
| 24 | `fc_qty1` | decimal(19,8) | NO |
| 25 | `fc_qty2` | decimal(19,8) | NO |
| 26 | `fc_src` | varchar(2) | NO |
| 27 | `fc_src_nbr` | varchar(15) | NO |
| 28 | `fc_src_lot` | varchar(18) | NO |
| 29 | `fc_src_cust` | varchar(255) | NO |

### `dbo.fcd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fcd_nbr` | varchar(15) | NO |
| 2 | `fcd_line` | int(10,0) | NO |
| 3 | `fcd_part` | varchar(30) | NO |
| 4 | `fcd_um` | varchar(4) | NO |
| 5 | `fcd_um_rate_m` | decimal(19,8) | NO |
| 6 | `fcd_um_rate_d` | decimal(19,8) | NO |
| 7 | `fcd_qty_fcs` | numeric(19,8) | NO |
| 8 | `fcd_req_date` | datetime | NO |
| 9 | `fcd_qty_con` | numeric(19,8) | NO |
| 10 | `fcd_rmks` | varchar(255) | NO |
| 11 | `fcd_closed` | bit | NO |
| 12 | `fcd_closed_by` | varchar(12) | NO |
| 13 | `fcd_closed_date` | datetime | YES |
| 14 | `fcd_crt_by` | varchar(12) | NO |
| 15 | `fcd_crt_date` | datetime | NO |
| 16 | `fcd_mod_times` | int(10,0) | NO |
| 17 | `fcd_mod_by` | varchar(12) | NO |
| 18 | `fcd_mod_date` | datetime | NO |
| 19 | `fcd_char1` | varchar(255) | NO |
| 20 | `fcd_char2` | varchar(255) | NO |
| 21 | `fcd_char3` | varchar(255) | NO |
| 22 | `fcd_char4` | varchar(255) | NO |
| 23 | `fcd_char5` | varchar(255) | NO |
| 24 | `fcd_char6` | varchar(255) | NO |
| 25 | `fcd_qty1` | decimal(19,8) | NO |
| 26 | `fcd_qty2` | decimal(19,8) | NO |
| 27 | `fcd_fc_date` | datetime | NO |
| 28 | `fcd_cust_part` | varchar(50) | NO |

### `dbo.fcg_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fcg_company` | varchar(8) | NO |
| 2 | `fcg_nbr` | varchar(15) | NO |
| 3 | `fcg_date` | datetime | NO |
| 4 | `fcg_type` | varchar(1) | NO |
| 5 | `fcg_chg_type` | varchar(10) | NO |
| 6 | `fcg_d_c` | varchar(1) | NO |
| 7 | `fcg_fas_code` | varchar(15) | NO |
| 8 | `fcg_o_qty` | numeric(19,8) | NO |
| 9 | `fcg_o_amt_base` | numeric(19,8) | NO |
| 10 | `fcg_o_amt_imprv` | numeric(19,8) | NO |
| 11 | `fcg_o_tot_dpc_amt` | numeric(19,8) | NO |
| 12 | `fcg_o_net_rate` | decimal(19,8) | NO |
| 13 | `fcg_o_net_value` | numeric(19,8) | NO |
| 14 | `fcg_o_amt_impm` | numeric(19,8) | NO |
| 15 | `fcg_o_life_mth` | int(10,0) | NO |
| 16 | `fcg_o_used_mth` | int(10,0) | NO |
| 17 | `fcg_o_work_qty` | numeric(19,8) | NO |
| 18 | `fcg_o_used_qty` | numeric(19,8) | NO |
| 19 | `fcg_o_dept` | varchar(10) | NO |
| 20 | `fcg_o_keeper` | varchar(12) | NO |
| 21 | `fcg_o_place` | varchar(30) | NO |
| 22 | `fcg_o_ac_code1` | varchar(15) | NO |
| 23 | `fcg_o_ac_code2` | varchar(15) | NO |
| 24 | `fcg_o_ac_code3` | varchar(15) | NO |
| 25 | `fcg_o_ac_code4` | varchar(15) | NO |
| 26 | `fcg_o_status` | varchar(1) | NO |
| 27 | `fcg_o_dpc` | bit | NO |
| 28 | `fcg_o_dpc_method` | varchar(1) | NO |
| 29 | `fcg_n_qty` | numeric(19,8) | NO |
| 30 | `fcg_n_amt_base` | numeric(19,8) | NO |
| 31 | `fcg_n_amt_imprv` | numeric(19,8) | NO |
| 32 | `fcg_n_tot_dpc_amt` | numeric(19,8) | NO |
| 33 | `fcg_n_net_rate` | decimal(19,8) | NO |
| 34 | `fcg_n_net_value` | numeric(19,8) | NO |
| 35 | `fcg_n_amt_impm` | numeric(19,8) | NO |
| 36 | `fcg_n_life_mth` | int(10,0) | NO |
| 37 | `fcg_n_used_mth` | int(10,0) | NO |
| 38 | `fcg_n_work_qty` | numeric(19,8) | NO |
| 39 | `fcg_n_used_qty` | numeric(19,8) | NO |
| 40 | `fcg_n_dept` | varchar(10) | NO |
| 41 | `fcg_n_keeper` | varchar(12) | NO |
| 42 | `fcg_n_place` | varchar(30) | NO |
| 43 | `fcg_n_ac_code1` | varchar(15) | NO |
| 44 | `fcg_n_ac_code2` | varchar(15) | NO |
| 45 | `fcg_n_ac_code3` | varchar(15) | NO |
| 46 | `fcg_n_ac_code4` | varchar(15) | NO |
| 47 | `fcg_n_status` | varchar(1) | NO |
| 48 | `fcg_n_dpc` | bit | NO |
| 49 | `fcg_n_dpc_method` | varchar(1) | NO |
| 50 | `fcg_amt_income` | numeric(19,8) | NO |
| 51 | `fcg_vat_rate` | decimal(19,8) | NO |
| 52 | `fcg_amt_vat` | numeric(19,8) | NO |
| 53 | `fcg_amt_lqd` | numeric(19,8) | NO |
| 54 | `fcg_rmks` | varchar(255) | NO |
| 55 | `fcg_vo_nbr` | varchar(15) | NO |
| 56 | `fcg_crt_by` | varchar(12) | NO |
| 57 | `fcg_crt_date` | datetime | NO |
| 58 | `fcg_mod_times` | int(10,0) | NO |
| 59 | `fcg_mod_by` | varchar(12) | NO |
| 60 | `fcg_mod_date` | datetime | NO |
| 61 | `fcg_pst` | bit | NO |
| 62 | `fcg_pst_by` | varchar(12) | NO |
| 63 | `fcg_pst_date` | datetime | YES |
| 64 | `fcg_char1` | varchar(255) | NO |
| 65 | `fcg_char2` | varchar(255) | NO |
| 66 | `fcg_char3` | varchar(255) | NO |
| 67 | `fcg_char4` | varchar(255) | NO |
| 68 | `fcg_char5` | varchar(255) | NO |
| 69 | `fcg_char6` | varchar(255) | NO |
| 70 | `fcg_qty1` | decimal(19,8) | NO |
| 71 | `fcg_qty2` | decimal(19,8) | NO |

### `dbo.fdpd2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fdpd2_nbr` | varchar(15) | NO |
| 2 | `fdpd2_line` | int(10,0) | NO |
| 3 | `fdpd2_dept` | varchar(10) | NO |
| 4 | `fdpd2_rate` | decimal(19,8) | NO |
| 5 | `fdpd2_ac_code1` | varchar(15) | NO |
| 6 | `fdpd2_ac_code2` | varchar(15) | NO |
| 7 | `fdpd2_ac_code3` | varchar(15) | NO |
| 8 | `fdpd2_rmks` | varchar(255) | NO |
| 9 | `fdpd2_crt_by` | varchar(12) | NO |
| 10 | `fdpd2_crt_date` | datetime | NO |
| 11 | `fdpd2_mod_times` | int(10,0) | NO |
| 12 | `fdpd2_mod_by` | varchar(12) | NO |
| 13 | `fdpd2_mod_date` | datetime | NO |
| 14 | `fdpd2_char1` | varchar(255) | NO |
| 15 | `fdpd2_char2` | varchar(255) | NO |
| 16 | `fdpd2_char3` | varchar(255) | NO |
| 17 | `fdpd2_char4` | varchar(255) | NO |
| 18 | `fdpd2_char5` | varchar(255) | NO |
| 19 | `fdpd2_char6` | varchar(255) | NO |
| 20 | `fdpd2_qty1` | decimal(19,8) | NO |
| 21 | `fdpd2_qty2` | decimal(19,8) | NO |

### `dbo.fgm_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fgm_site` | varchar(8) | NO |
| 2 | `fgm_year` | int(10,0) | NO |
| 3 | `fgm_month` | int(10,0) | NO |
| 4 | `fgm_part` | varchar(30) | NO |
| 5 | `fgm_stkin_qty` | numeric(19,8) | NO |
| 6 | `fgm_subin_qty` | numeric(19,8) | NO |
| 7 | `fgm_mtl_amt` | numeric(19,8) | NO |
| 8 | `fgm_lbr_amt` | numeric(19,8) | NO |
| 9 | `fgm_bdn_amt` | numeric(19,8) | NO |
| 10 | `fgm_sub_amt` | numeric(19,8) | NO |
| 11 | `fgm_mtlll_amt` | numeric(19,8) | NO |
| 12 | `fgm_lbrll_amt` | numeric(19,8) | NO |
| 13 | `fgm_bdnll_amt` | numeric(19,8) | NO |
| 14 | `fgm_subll_amt` | numeric(19,8) | NO |
| 15 | `fgm_crt_by` | varchar(12) | NO |
| 16 | `fgm_crt_date` | datetime | NO |
| 17 | `fgm_mod_times` | int(10,0) | NO |
| 18 | `fgm_mod_by` | varchar(12) | NO |
| 19 | `fgm_mod_date` | datetime | NO |
| 20 | `fgm_char1` | varchar(255) | NO |
| 21 | `fgm_char2` | varchar(255) | NO |
| 22 | `fgm_char3` | varchar(255) | NO |
| 23 | `fgm_char4` | varchar(255) | NO |
| 24 | `fgm_char5` | varchar(255) | NO |
| 25 | `fgm_char6` | varchar(255) | NO |
| 26 | `fgm_qty1` | decimal(19,8) | NO |
| 27 | `fgm_qty2` | decimal(19,8) | NO |

### `dbo.fgr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fgr_fgr` | varchar(15) | NO |
| 2 | `fgr_date` | datetime | NO |
| 3 | `fgr_loc` | varchar(8) | NO |
| 4 | `fgr_rmks` | varchar(255) | NO |
| 5 | `fgr_wf_status` | varchar(1) | NO |
| 6 | `fgr_site` | varchar(8) | NO |
| 7 | `fgr_prog_code` | varchar(12) | NO |
| 8 | `fgr_doc_code` | varchar(12) | NO |
| 9 | `fgr_crt_by` | varchar(12) | NO |
| 10 | `fgr_crt_date` | datetime | NO |
| 11 | `fgr_mod_times` | int(10,0) | NO |
| 12 | `fgr_mod_by` | varchar(12) | NO |
| 13 | `fgr_mod_date` | datetime | NO |
| 14 | `fgr_pst` | bit | NO |
| 15 | `fgr_pst_by` | varchar(12) | NO |
| 16 | `fgr_pst_date` | datetime | YES |
| 17 | `fgr_char1` | varchar(255) | NO |
| 18 | `fgr_char2` | varchar(255) | NO |
| 19 | `fgr_char3` | varchar(255) | NO |
| 20 | `fgr_char4` | varchar(255) | NO |
| 21 | `fgr_char5` | varchar(255) | NO |
| 22 | `fgr_char6` | varchar(255) | NO |
| 23 | `fgr_qty1` | decimal(19,8) | NO |
| 24 | `fgr_qty2` | decimal(19,8) | NO |
| 25 | `fgr_chk` | bit | NO |
| 26 | `fgr_chk_by` | varchar(12) | NO |
| 27 | `fgr_chk_date` | datetime | YES |
| 28 | `fgr_data_src` | varchar(1) | NO |
| 29 | `fgr_data_id` | varchar(255) | NO |

### `dbo.fgrd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fgrd_fgr` | varchar(15) | NO |
| 2 | `fgrd_line` | int(10,0) | NO |
| 3 | `fgrd_wo_nbr` | varchar(15) | NO |
| 4 | `fgrd_wo_lot` | varchar(18) | NO |
| 5 | `fgrd_part` | varchar(30) | NO |
| 6 | `fgrd_type` | varchar(1) | NO |
| 7 | `fgrd_qty` | numeric(19,8) | NO |
| 8 | `fgrd_loc` | varchar(8) | NO |
| 9 | `fgrd_lot` | varchar(18) | NO |
| 10 | `fgrd_grade` | varchar(2) | NO |
| 11 | `fgrd_rmks` | varchar(255) | NO |
| 12 | `fgrd_site` | varchar(8) | NO |
| 13 | `fgrd_crt_by` | varchar(12) | NO |
| 14 | `fgrd_crt_date` | datetime | NO |
| 15 | `fgrd_mod_times` | int(10,0) | NO |
| 16 | `fgrd_mod_by` | varchar(12) | NO |
| 17 | `fgrd_mod_date` | datetime | NO |
| 18 | `fgrd_char1` | varchar(255) | NO |
| 19 | `fgrd_char2` | varchar(255) | NO |
| 20 | `fgrd_char3` | varchar(255) | NO |
| 21 | `fgrd_char4` | varchar(255) | NO |
| 22 | `fgrd_char5` | varchar(255) | NO |
| 23 | `fgrd_char6` | varchar(255) | NO |
| 24 | `fgrd_qty1` | decimal(19,8) | NO |
| 25 | `fgrd_qty2` | decimal(19,8) | NO |
| 26 | `fgrd_data_src` | varchar(1) | NO |
| 27 | `fgrd_data_id` | varchar(255) | NO |

### `dbo.fty_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `fty_code` | varchar(15) | NO |
| 2 | `fty_name` | varchar(50) | NO |
| 3 | `fty_life_mth` | int(10,0) | NO |
| 4 | `fty_work_qty` | numeric(19,8) | NO |
| 5 | `fty_um` | varchar(4) | NO |
| 6 | `fty_net_rate` | decimal(19,8) | NO |
| 7 | `fty_dpc` | varchar(1) | NO |
| 8 | `fty_dpc_method` | varchar(1) | NO |
| 9 | `fty_ac_code1` | varchar(15) | NO |
| 10 | `fty_ac_code2` | varchar(15) | NO |
| 11 | `fty_ac_code3` | varchar(15) | NO |
| 12 | `fty_ac_code4` | varchar(15) | NO |
| 13 | `fty_code_rule` | varchar(15) | NO |
| 14 | `fty_crt_by` | varchar(12) | NO |
| 15 | `fty_crt_date` | datetime | NO |
| 16 | `fty_mod_times` | int(10,0) | NO |
| 17 | `fty_mod_by` | varchar(12) | NO |
| 18 | `fty_mod_date` | datetime | NO |
| 19 | `fty_char1` | varchar(255) | NO |
| 20 | `fty_char2` | varchar(255) | NO |
| 21 | `fty_char3` | varchar(255) | NO |
| 22 | `fty_char4` | varchar(255) | NO |
| 23 | `fty_char5` | varchar(255) | NO |
| 24 | `fty_char6` | varchar(255) | NO |
| 25 | `fty_qty1` | decimal(19,8) | NO |
| 26 | `fty_qty2` | decimal(19,8) | NO |

### `dbo.gcw1_pts` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `gcw1_flow_no` | int(10,0) | NO |
| 2 | `gcw1_user_id` | varchar(12) | NO |
| 3 | `gcw1_par` | varchar(30) | NO |
| 4 | `gcw1_comp` | varchar(30) | NO |
| 5 | `gcw1_sub_part` | varchar(30) | NO |
| 6 | `gcw1_qty_m` | numeric(19,8) | NO |
| 7 | `gcw1_qty_d` | numeric(19,8) | NO |
| 8 | `gcw1_priority` | int(10,0) | NO |
| 9 | `gcw1_qty_exec` | numeric(19,8) | NO |
| 10 | `gcw1_qty_unalloc` | numeric(19,8) | NO |

### `dbo.gend_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `gend_gen` | varchar(30) | NO |
| 2 | `gend_option` | varchar(30) | NO |
| 3 | `gend_name` | varchar(255) | NO |
| 4 | `gend_property1` | varchar(255) | NO |
| 5 | `gend_property2` | varchar(255) | NO |
| 6 | `gend_property3` | varchar(255) | NO |
| 7 | `gend_property4` | varchar(255) | NO |
| 8 | `gend_disabled` | bit | NO |
| 9 | `gend_crt_by` | varchar(12) | NO |
| 10 | `gend_crt_date` | datetime | NO |
| 11 | `gend_char1` | varchar(255) | NO |
| 12 | `gend_char2` | varchar(255) | NO |
| 13 | `gend_char3` | varchar(255) | NO |
| 14 | `gend_char4` | varchar(255) | NO |
| 15 | `gend_char5` | varchar(255) | NO |
| 16 | `gend_char6` | varchar(255) | NO |
| 17 | `gend_qty1` | decimal(19,8) | NO |
| 18 | `gend_qty2` | decimal(19,8) | NO |
| 19 | `gend_property5` | varchar(255) | NO |
| 20 | `gend_property6` | varchar(255) | NO |
| 21 | `gend_property7` | varchar(255) | NO |
| 22 | `gend_property8` | varchar(255) | NO |
| 23 | `gend_property9` | varchar(255) | NO |
| 24 | `gend_property10` | numeric(19,8) | NO |
| 25 | `gend_property11` | numeric(19,8) | NO |
| 26 | `gend_property12` | numeric(19,8) | NO |
| 27 | `gend_property13` | numeric(19,8) | NO |
| 28 | `gend_property14` | numeric(19,8) | NO |
| 29 | `gend_property15` | numeric(19,8) | NO |
| 30 | `gend_property16` | datetime | YES |
| 31 | `gend_property17` | datetime | YES |

### `dbo.gend_detbak` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `gend_gen` | varchar(30) | NO |
| 2 | `gend_option` | varchar(30) | NO |
| 3 | `gend_name` | varchar(255) | NO |
| 4 | `gend_property1` | varchar(255) | NO |
| 5 | `gend_property2` | varchar(255) | NO |
| 6 | `gend_property3` | varchar(255) | NO |
| 7 | `gend_property4` | varchar(255) | NO |
| 8 | `gend_disabled` | bit | NO |
| 9 | `gend_crt_by` | varchar(12) | NO |
| 10 | `gend_crt_date` | datetime | NO |
| 11 | `gend_char1` | varchar(255) | NO |
| 12 | `gend_char2` | varchar(255) | NO |
| 13 | `gend_char3` | varchar(255) | NO |
| 14 | `gend_char4` | varchar(255) | NO |
| 15 | `gend_char5` | varchar(255) | NO |
| 16 | `gend_char6` | varchar(255) | NO |
| 17 | `gend_qty1` | decimal(19,8) | NO |
| 18 | `gend_qty2` | decimal(19,8) | NO |
| 19 | `gend_property5` | varchar(255) | NO |
| 20 | `gend_property6` | varchar(255) | NO |
| 21 | `gend_property7` | varchar(255) | NO |
| 22 | `gend_property8` | varchar(255) | NO |
| 23 | `gend_property9` | varchar(255) | NO |
| 24 | `gend_property10` | numeric(19,8) | NO |
| 25 | `gend_property11` | numeric(19,8) | NO |
| 26 | `gend_property12` | numeric(19,8) | NO |
| 27 | `gend_property13` | numeric(19,8) | NO |
| 28 | `gend_property14` | numeric(19,8) | NO |
| 29 | `gend_property15` | numeric(19,8) | NO |
| 30 | `gend_property16` | datetime | YES |
| 31 | `gend_property17` | datetime | YES |

### `dbo.grn_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `grn_grn` | varchar(15) | NO |
| 2 | `grn_date` | datetime | NO |
| 3 | `grn_vend` | varchar(8) | NO |
| 4 | `grn_ps_nbr` | varchar(30) | NO |
| 5 | `grn_loc_iqc` | varchar(8) | NO |
| 6 | `grn_loc_raw` | varchar(8) | NO |
| 7 | `grn_rmks` | varchar(255) | NO |
| 8 | `grn_wf_status` | varchar(1) | NO |
| 9 | `grn_site` | varchar(8) | NO |
| 10 | `grn_prog_code` | varchar(12) | NO |
| 11 | `grn_doc_code` | varchar(12) | NO |
| 12 | `grn_crt_by` | varchar(12) | NO |
| 13 | `grn_crt_date` | datetime | NO |
| 14 | `grn_mod_times` | int(10,0) | NO |
| 15 | `grn_mod_by` | varchar(12) | NO |
| 16 | `grn_mod_date` | datetime | NO |
| 17 | `grn_pst` | bit | NO |
| 18 | `grn_pst_by` | varchar(12) | NO |
| 19 | `grn_pst_date` | datetime | YES |
| 20 | `grn_char1` | varchar(255) | NO |
| 21 | `grn_char2` | varchar(255) | NO |
| 22 | `grn_char3` | varchar(255) | NO |
| 23 | `grn_char4` | varchar(255) | NO |
| 24 | `grn_char5` | varchar(255) | NO |
| 25 | `grn_char6` | varchar(255) | NO |
| 26 | `grn_qty1` | decimal(19,8) | NO |
| 27 | `grn_qty2` | decimal(19,8) | NO |
| 28 | `grn_data_src` | varchar(1) | NO |
| 29 | `grn_data_id` | varchar(255) | NO |
| 30 | `grn_chk` | bit | NO |
| 31 | `grn_chk_by` | varchar(12) | NO |
| 32 | `grn_chk_date` | datetime | YES |
| 33 | `grn_cfm` | bit | NO |
| 34 | `grn_cfm_by` | varchar(12) | NO |
| 35 | `grn_cfm_name` | varchar(30) | NO |
| 36 | `grn_cfm_date` | datetime | YES |
| 37 | `grn_crt_name` | varchar(30) | NO |
| 38 | `grn_mod_name` | varchar(30) | NO |
| 39 | `grn_pst_name` | varchar(30) | NO |

### `dbo.grnd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `grnd_grn` | varchar(15) | NO |
| 2 | `grnd_line` | int(10,0) | NO |
| 3 | `grnd_site` | varchar(8) | NO |
| 4 | `grnd_loc` | varchar(8) | NO |
| 5 | `grnd_po` | varchar(15) | NO |
| 6 | `grnd_po_line` | int(10,0) | NO |
| 7 | `grnd_part` | varchar(30) | NO |
| 8 | `grnd_qty_ord` | numeric(19,8) | NO |
| 9 | `grnd_qty_spare` | numeric(19,8) | NO |
| 10 | `grnd_qty_rcvd` | numeric(19,8) | NO |
| 11 | `grnd_qty_spare_rcvd` | numeric(19,8) | NO |
| 12 | `grnd_qty_pending` | numeric(19,8) | NO |
| 13 | `grnd_um` | varchar(4) | NO |
| 14 | `grnd_um_rate_m` | decimal(19,8) | NO |
| 15 | `grnd_um_rate_d` | decimal(19,8) | NO |
| 16 | `grnd_lot` | varchar(18) | NO |
| 17 | `grnd_rmks` | varchar(255) | NO |
| 18 | `grnd_crt_by` | varchar(12) | NO |
| 19 | `grnd_crt_date` | datetime | NO |
| 20 | `grnd_mod_times` | int(10,0) | NO |
| 21 | `grnd_mod_by` | varchar(12) | NO |
| 22 | `grnd_mod_date` | datetime | NO |
| 23 | `grnd_char1` | varchar(255) | NO |
| 24 | `grnd_char2` | varchar(255) | NO |
| 25 | `grnd_char3` | varchar(255) | NO |
| 26 | `grnd_char4` | varchar(255) | NO |
| 27 | `grnd_char5` | varchar(255) | NO |
| 28 | `grnd_char6` | varchar(255) | NO |
| 29 | `grnd_qty1` | decimal(19,8) | NO |
| 30 | `grnd_qty2` | decimal(19,8) | NO |
| 31 | `grnd_qty_rcvd_inv` | numeric(19,8) | NO |
| 32 | `grnd_qty_spare_rcvd_inv` | numeric(19,8) | NO |
| 33 | `grnd_qty_pending_inv` | numeric(19,8) | NO |
| 34 | `grnd_data_src` | varchar(1) | NO |
| 35 | `grnd_data_id` | varchar(255) | NO |
| 36 | `grnd_crt_name` | varchar(30) | NO |
| 37 | `grnd_mod_name` | varchar(30) | NO |

### `dbo.grpd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `grpd_code` | varchar(12) | NO |
| 2 | `grpd_prog` | varchar(12) | NO |
| 3 | `grpd_run` | bit | NO |
| 4 | `grpd_insert` | bit | NO |
| 5 | `grpd_modify` | bit | NO |
| 6 | `grpd_delete` | bit | NO |
| 7 | `grpd_print` | bit | NO |
| 8 | `grpd_export` | bit | NO |
| 9 | `grpd_pst` | bit | NO |
| 10 | `grpd_unpst` | bit | NO |
| 11 | `grpd_chk` | bit | NO |
| 12 | `grpd_unchk` | bit | NO |
| 13 | `grpd_wf_submit` | bit | NO |
| 14 | `grpd_wf_cancel` | bit | NO |
| 15 | `grpd_view_cost` | bit | NO |
| 16 | `grpd_view_others` | bit | NO |
| 17 | `grpd_mod_others` | bit | NO |
| 18 | `grpd_del_others` | bit | NO |
| 19 | `grpd_design` | bit | NO |
| 20 | `grpd_negative` | bit | NO |
| 21 | `grpd_perm1` | bit | NO |
| 22 | `grpd_perm2` | bit | NO |
| 23 | `grpd_perm3` | bit | NO |
| 24 | `grpd_perm4` | bit | NO |
| 25 | `grpd_perm5` | bit | NO |
| 26 | `grpd_perm6` | bit | NO |
| 27 | `grpd_char1` | varchar(255) | NO |
| 28 | `grpd_char2` | varchar(255) | NO |
| 29 | `grpd_char3` | varchar(255) | NO |
| 30 | `grpd_char4` | varchar(255) | NO |
| 31 | `grpd_char5` | varchar(255) | NO |
| 32 | `grpd_char6` | varchar(255) | NO |
| 33 | `grpd_qty1` | decimal(19,8) | NO |
| 34 | `grpd_qty2` | decimal(19,8) | NO |
| 35 | `grpd_invld` | bit | NO |
| 36 | `grpd_uninvld` | bit | NO |
| 37 | `grpd_att_insert` | bit | NO |
| 38 | `grpd_att_view` | bit | NO |
| 39 | `grpd_att_view_oth` | bit | NO |
| 40 | `grpd_att_download` | bit | NO |
| 41 | `grpd_att_down_oth` | bit | NO |
| 42 | `grpd_att_del` | bit | NO |
| 43 | `grpd_att_del_oth` | bit | NO |
| 44 | `grpd_perm7` | bit | NO |
| 45 | `grpd_perm8` | bit | NO |
| 46 | `grpd_perm9` | bit | NO |
| 47 | `grpd_rmks1` | varchar(255) | NO |
| 48 | `grpd_rmks2` | varchar(255) | NO |
| 49 | `grpd_rmks3` | varchar(255) | NO |
| 50 | `grpd_rmks4` | varchar(255) | NO |
| 51 | `grpd_rmks5` | varchar(255) | NO |
| 52 | `grpd_rmks6` | varchar(255) | NO |
| 53 | `grpd_rmks7` | varchar(255) | NO |
| 54 | `grpd_rmks8` | varchar(255) | NO |
| 55 | `grpd_rmks9` | varchar(255) | NO |
| 56 | `grpd_rmks` | varchar(255) | NO |
| 57 | `grpd_crt_by` | varchar(12) | NO |
| 58 | `grpd_crt_date` | datetime | YES |
| 59 | `grpd_mod_times` | int(10,0) | NO |
| 60 | `grpd_mod_by` | varchar(12) | NO |
| 61 | `grpd_mod_date` | datetime | YES |

### `dbo.hd_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `hd_site` | varchar(8) | NO |
| 2 | `hd_date` | datetime | NO |
| 3 | `hd_desc` | varchar(30) | NO |
| 4 | `hd_crt_by` | varchar(12) | NO |
| 5 | `hd_crt_date` | datetime | NO |
| 6 | `hd_char1` | varchar(255) | NO |
| 7 | `hd_char2` | varchar(255) | NO |
| 8 | `hd_char3` | varchar(255) | NO |
| 9 | `hd_char4` | varchar(255) | NO |
| 10 | `hd_char5` | varchar(255) | NO |
| 11 | `hd_char6` | varchar(255) | NO |
| 12 | `hd_qty1` | decimal(19,8) | NO |
| 13 | `hd_qty2` | decimal(19,8) | NO |

### `dbo.hremp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `hremp_code` | varchar(15) | NO |
| 2 | `hremp_cname` | varchar(50) | NO |
| 3 | `hremp_ename` | varchar(50) | NO |
| 4 | `hremp_aid_code` | varchar(10) | NO |
| 5 | `hremp_dept` | varchar(10) | NO |
| 6 | `hremp_dept2` | varchar(30) | NO |
| 7 | `hremp_position` | varchar(15) | NO |
| 8 | `hremp_trades` | varchar(30) | NO |
| 9 | `hremp_id_type` | varchar(30) | NO |
| 10 | `hremp_id_num` | varchar(30) | NO |
| 11 | `hremp_id_valid` | datetime | NO |
| 12 | `hremp_id_by` | varchar(80) | NO |
| 13 | `hremp_birthday` | datetime | NO |
| 14 | `hremp_gender` | varchar(1) | NO |
| 15 | `hremp_nation` | varchar(30) | NO |
| 16 | `hremp_hometown` | varchar(30) | NO |
| 17 | `hremp_relegion` | varchar(30) | NO |
| 18 | `hremp_marital` | varchar(1) | NO |
| 19 | `hremp_diploma` | varchar(30) | NO |
| 20 | `hremp_school` | varchar(50) | NO |
| 21 | `hremp_major` | varchar(30) | NO |
| 22 | `hremp_grd_date` | datetime | YES |
| 23 | `hremp_prof` | varchar(30) | NO |
| 24 | `hremp_prof_date` | datetime | YES |
| 25 | `hremp_fore_lang` | varchar(30) | NO |
| 26 | `hremp_fore_lvl` | varchar(30) | NO |
| 27 | `hremp_tele` | varchar(50) | NO |
| 28 | `hremp_email` | varchar(80) | NO |
| 29 | `hremp_oth_con` | varchar(80) | NO |
| 30 | `hremp_labor_num` | varchar(50) | NO |
| 31 | `hremp_enter_date` | datetime | NO |
| 32 | `hremp_cont_from` | datetime | YES |
| 33 | `hremp_cont_to` | datetime | YES |
| 34 | `hremp_cont_type` | varchar(30) | NO |
| 35 | `hremp_trail_from` | datetime | YES |
| 36 | `hremp_trail_to` | datetime | YES |
| 37 | `hremp_offi_date` | datetime | YES |
| 38 | `hremp_source` | varchar(30) | NO |
| 39 | `hremp_intr_by` | varchar(30) | NO |
| 40 | `hremp_deposit` | numeric(19,8) | NO |
| 41 | `hremp_status` | varchar(1) | NO |
| 42 | `hremp_leave_date` | datetime | YES |
| 43 | `hremp_leave_rsn` | varchar(30) | NO |
| 44 | `hremp_home_add` | varchar(255) | NO |
| 45 | `hremp_home_zip` | varchar(10) | NO |
| 46 | `hremp_home_cont` | varchar(30) | NO |
| 47 | `hremp_home_tele` | varchar(50) | NO |
| 48 | `hremp_curr_add` | varchar(255) | NO |
| 49 | `hremp_curr_zip` | varchar(10) | NO |
| 50 | `hremp_emgn_cont` | varchar(30) | NO |
| 51 | `hremp_emgn_tele` | varchar(50) | NO |
| 52 | `hremp_dorm_num` | varchar(10) | NO |
| 53 | `hremp_sly_level` | varchar(10) | NO |
| 54 | `hremp_sly_rmks` | varchar(255) | NO |
| 55 | `hremp_pension` | varchar(30) | NO |
| 56 | `hremp_medical` | varchar(30) | NO |
| 57 | `hremp_unemploy` | varchar(30) | NO |
| 58 | `hremp_provident` | varchar(30) | NO |
| 59 | `hremp_bank_acc1` | varchar(30) | NO |
| 60 | `hremp_bank_acc2` | varchar(30) | NO |
| 61 | `hremp_rule` | varchar(10) | NO |
| 62 | `hremp_need_card` | bit | NO |
| 63 | `hremp_card_id` | varchar(50) | NO |
| 64 | `hremp_card_date` | datetime | YES |
| 65 | `hremp_sch` | varchar(15) | NO |
| 66 | `hremp_photo` | image(2147483647) | YES |
| 67 | `hremp_rmks` | varchar(255) | NO |
| 68 | `hremp_crt_by` | varchar(12) | NO |
| 69 | `hremp_crt_date` | datetime | NO |
| 70 | `hremp_mod_times` | int(10,0) | NO |
| 71 | `hremp_mod_by` | varchar(12) | NO |
| 72 | `hremp_mod_date` | datetime | NO |
| 73 | `hremp_pst` | bit | NO |
| 74 | `hremp_pst_by` | varchar(12) | NO |
| 75 | `hremp_pst_date` | datetime | YES |
| 76 | `hremp_char1` | varchar(255) | NO |
| 77 | `hremp_char2` | varchar(255) | NO |
| 78 | `hremp_char3` | varchar(255) | NO |
| 79 | `hremp_char4` | varchar(255) | NO |
| 80 | `hremp_char5` | varchar(255) | NO |
| 81 | `hremp_char6` | varchar(255) | NO |
| 82 | `hremp_char7` | varchar(255) | NO |
| 83 | `hremp_char8` | varchar(255) | NO |
| 84 | `hremp_char9` | varchar(255) | NO |
| 85 | `hremp_qty1` | decimal(19,8) | NO |
| 86 | `hremp_qty2` | decimal(19,8) | NO |
| 87 | `hremp_qty3` | decimal(19,8) | NO |
| 88 | `hremp_qty4` | decimal(19,8) | NO |
| 89 | `hremp_qty5` | decimal(19,8) | NO |
| 90 | `hremp_qty6` | decimal(19,8) | NO |

### `dbo.hrpo_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `hrpo_code` | varchar(15) | NO |
| 2 | `hrpo_name` | varchar(50) | NO |
| 3 | `hrpo_trail` | int(10,0) | NO |
| 4 | `hrpo_um` | varchar(1) | NO |
| 5 | `hrpo_rmks` | varchar(255) | NO |
| 6 | `hrpo_crt_by` | varchar(12) | NO |
| 7 | `hrpo_crt_date` | datetime | NO |
| 8 | `hrpo_mod_times` | int(10,0) | NO |
| 9 | `hrpo_mod_by` | varchar(12) | NO |
| 10 | `hrpo_mod_date` | datetime | NO |
| 11 | `hrpo_char1` | varchar(255) | NO |
| 12 | `hrpo_char2` | varchar(255) | NO |
| 13 | `hrpo_char3` | varchar(255) | NO |
| 14 | `hrpo_char4` | varchar(255) | NO |
| 15 | `hrpo_char5` | varchar(255) | NO |
| 16 | `hrpo_char6` | varchar(255) | NO |
| 17 | `hrpo_qty1` | decimal(19,8) | NO |
| 18 | `hrpo_qty2` | decimal(19,8) | NO |

### `dbo.hrtr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `hrtr_nbr` | varchar(15) | NO |
| 2 | `hrtr_date` | datetime | NO |
| 3 | `hrtr_eff_date` | datetime | NO |
| 4 | `hrtr_emp` | varchar(15) | NO |
| 5 | `hrtr_type` | varchar(30) | NO |
| 6 | `hrtr_reason` | varchar(255) | NO |
| 7 | `hrtr_bf_dept` | varchar(10) | NO |
| 8 | `hrtr_bf_dept2` | varchar(30) | NO |
| 9 | `hrtr_bf_pos` | varchar(15) | NO |
| 10 | `hrtr_bf_trades` | varchar(30) | NO |
| 11 | `hrtr_bf_prof` | varchar(30) | NO |
| 12 | `hrtr_bf_prof_date` | datetime | YES |
| 13 | `hrtr_af_dept` | varchar(10) | NO |
| 14 | `hrtr_af_dept2` | varchar(30) | NO |
| 15 | `hrtr_af_pos` | varchar(15) | NO |
| 16 | `hrtr_af_trades` | varchar(30) | NO |
| 17 | `hrtr_af_prof` | varchar(30) | NO |
| 18 | `hrtr_af_prof_date` | datetime | YES |
| 19 | `hrtr_rmks` | varchar(255) | NO |
| 20 | `hrtr_crt_by` | varchar(12) | NO |
| 21 | `hrtr_crt_date` | datetime | NO |
| 22 | `hrtr_mod_times` | int(10,0) | NO |
| 23 | `hrtr_mod_by` | varchar(12) | NO |
| 24 | `hrtr_mod_date` | datetime | NO |
| 25 | `hrtr_pst` | bit | NO |
| 26 | `hrtr_pst_by` | varchar(12) | NO |
| 27 | `hrtr_pst_date` | datetime | YES |
| 28 | `hrtr_char1` | varchar(255) | NO |
| 29 | `hrtr_char2` | varchar(255) | NO |
| 30 | `hrtr_char3` | varchar(255) | NO |
| 31 | `hrtr_char4` | varchar(255) | NO |
| 32 | `hrtr_char5` | varchar(255) | NO |
| 33 | `hrtr_char6` | varchar(255) | NO |
| 34 | `hrtr_qty1` | decimal(19,8) | NO |
| 35 | `hrtr_qty2` | decimal(19,8) | NO |

### `dbo.import_pc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_pc_flow` | int(10,0) | NO |
| 2 | `tmp_pc_nbr` | varchar(15) | NO |
| 3 | `tmp_pc_vend` | varchar(8) | NO |
| 4 | `tmp_pc_curr` | varchar(4) | NO |
| 5 | `tmp_pc_part` | varchar(30) | NO |
| 6 | `tmp_pc_um` | varchar(4) | NO |
| 7 | `tmp_pc_um_rate_m` | decimal(19,8) | NO |
| 8 | `tmp_pc_um_rate_d` | decimal(19,8) | NO |
| 9 | `tmp_pc_start` | datetime | NO |
| 10 | `tmp_pc_expire` | datetime | NO |
| 11 | `tmp_pc_vat_incl` | bit | NO |
| 12 | `tmp_pc_vat` | decimal(19,8) | NO |
| 13 | `tmp_pc_type` | varchar(1) | NO |
| 14 | `tmp_pc_price_mtl` | decimal(19,8) | NO |
| 15 | `tmp_pc_price_sub` | decimal(19,8) | NO |
| 16 | `tmp_pc_price` | decimal(19,8) | NO |
| 17 | `tmp_pc_ord_min` | numeric(19,8) | NO |
| 18 | `tmp_pc_ord_mult` | numeric(19,8) | NO |
| 19 | `tmp_pc_pur_lt` | int(10,0) | NO |
| 20 | `tmp_pc_cu_curr` | varchar(4) | NO |
| 21 | `tmp_pc_prog_code` | varchar(12) | NO |
| 22 | `tmp_pc_qtype` | varchar(2) | NO |
| 23 | `tmp_pc_rmks` | varchar(255) | NO |
| 24 | `tmp_pc_wf_status` | varchar(1) | NO |
| 25 | `tmp_pc_crt_by` | varchar(12) | NO |
| 26 | `tmp_pc_crt_date` | datetime | NO |
| 27 | `tmp_pc_mod_times` | int(10,0) | NO |
| 28 | `tmp_pc_mod_by` | varchar(12) | NO |
| 29 | `tmp_pc_mod_date` | datetime | NO |
| 30 | `tmp_pc_pst` | bit | NO |
| 31 | `tmp_pc_pst_by` | varchar(12) | NO |
| 32 | `tmp_pc_pst_date` | datetime | YES |
| 33 | `tmp_pc_char1` | varchar(255) | NO |
| 34 | `tmp_pc_char2` | varchar(255) | NO |
| 35 | `tmp_pc_char3` | varchar(255) | NO |
| 36 | `tmp_pc_char4` | varchar(255) | NO |
| 37 | `tmp_pc_char5` | varchar(255) | NO |
| 38 | `tmp_pc_char6` | varchar(255) | NO |
| 39 | `tmp_pc_qty1` | decimal(19,8) | NO |
| 40 | `tmp_pc_qty2` | decimal(19,8) | NO |
| 41 | `tmp_pcd_price` | varchar(255) | NO |

### `dbo.import_pod_price` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `imp_pod_flow` | int(10,0) | NO |
| 2 | `imp_pod_nbr` | varchar(15) | NO |
| 3 | `imp_pod_line` | int(10,0) | NO |
| 4 | `imp_pod_part` | varchar(30) | NO |
| 5 | `imp_pod_pur_cost` | numeric(19,8) | NO |
| 6 | `imp_pod_mod_by` | varchar(12) | NO |
| 7 | `imp_pod_mod_date` | datetime | NO |
| 8 | `imp_pod_cost_old` | numeric(19,8) | NO |

### `dbo.import_sc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_sc_flow` | int(10,0) | NO |
| 2 | `tmp_sc_nbr` | varchar(15) | NO |
| 3 | `tmp_sc_cust` | varchar(8) | NO |
| 4 | `tmp_sc_curr` | varchar(4) | NO |
| 5 | `tmp_sc_part` | varchar(30) | NO |
| 6 | `tmp_sc_cust_part` | varchar(80) | NO |
| 7 | `tmp_sc_um` | varchar(4) | NO |
| 8 | `tmp_sc_um_rate_m` | decimal(19,8) | NO |
| 9 | `tmp_sc_um_rate_d` | decimal(19,8) | NO |
| 10 | `tmp_sc_start` | datetime | NO |
| 11 | `tmp_sc_expire` | datetime | NO |
| 12 | `tmp_sc_vat` | bit | NO |
| 13 | `tmp_sc_vat_rate` | decimal(19,8) | NO |
| 14 | `tmp_sc_disc` | decimal(19,8) | NO |
| 15 | `tmp_sc_ast_code` | varchar(15) | NO |
| 16 | `tmp_sc_spare_pct` | decimal(19,8) | NO |
| 17 | `tmp_sc_price` | decimal(19,8) | NO |
| 18 | `tmp_sc_rmks` | varchar(255) | NO |
| 19 | `tmp_sc_crt_by` | varchar(12) | NO |
| 20 | `tmp_sc_crt_date` | datetime | NO |
| 21 | `tmp_sc_wf_status` | varchar(1) | NO |
| 22 | `tmp_sc_mod_times` | int(10,0) | NO |
| 23 | `tmp_sc_mod_by` | varchar(12) | NO |
| 24 | `tmp_sc_mod_date` | datetime | NO |
| 25 | `tmp_sc_pst` | bit | NO |
| 26 | `tmp_sc_pst_by` | varchar(12) | NO |
| 27 | `tmp_sc_pst_date` | datetime | YES |
| 28 | `tmp_sc_char1` | varchar(255) | NO |
| 29 | `tmp_sc_char2` | varchar(255) | NO |
| 30 | `tmp_sc_char3` | varchar(255) | NO |
| 31 | `tmp_sc_char4` | varchar(255) | NO |
| 32 | `tmp_sc_char5` | varchar(255) | NO |
| 33 | `tmp_sc_char6` | varchar(255) | NO |
| 34 | `tmp_sc_qty1` | decimal(19,8) | NO |
| 35 | `tmp_sc_qty2` | decimal(19,8) | NO |
| 36 | `tmp_scd_price` | varchar(255) | NO |

### `dbo.import_sod_price` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `imp_sod_flow` | int(10,0) | NO |
| 2 | `imp_sod_nbr` | varchar(15) | NO |
| 3 | `imp_sod_line` | int(10,0) | NO |
| 4 | `imp_sod_part` | varchar(30) | NO |
| 5 | `imp_sod_price` | numeric(19,8) | NO |
| 6 | `imp_sod_mod_by` | varchar(12) | NO |
| 7 | `imp_sod_mod_date` | datetime | NO |
| 8 | `imp_sod_price_old` | numeric(19,8) | NO |

### `dbo.import_vchd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_vchd_user` | varchar(12) | NO |
| 2 | `tmp_vchd_nbr_code` | varchar(15) | NO |
| 3 | `tmp_vchd_nbr` | varchar(15) | NO |
| 4 | `tmp_vchd_line` | int(10,0) | NO |
| 5 | `tmp_vchd_ac_code` | varchar(15) | NO |
| 6 | `tmp_vchd_content` | varchar(255) | NO |
| 7 | `tmp_vchd_curr` | varchar(4) | NO |
| 8 | `tmp_vchd_ex_rate` | decimal(19,8) | NO |
| 9 | `tmp_vchd_price` | decimal(19,8) | NO |
| 10 | `tmp_vchd_debit_amt` | numeric(19,8) | NO |
| 11 | `tmp_vchd_debit_base` | numeric(19,8) | NO |
| 12 | `tmp_vchd_debit_qty` | numeric(19,8) | NO |
| 13 | `tmp_vchd_credit_amt` | numeric(19,8) | NO |
| 14 | `tmp_vchd_credit_base` | numeric(19,8) | NO |
| 15 | `tmp_vchd_credit_qty` | numeric(19,8) | NO |
| 16 | `tmp_vchd_dept` | varchar(10) | NO |
| 17 | `tmp_vchd_vt_code1` | varchar(30) | NO |
| 18 | `tmp_vchd_vt_name1` | varchar(255) | NO |
| 19 | `tmp_vchd_vt_code2` | varchar(30) | NO |
| 20 | `tmp_vchd_vt_name2` | varchar(255) | NO |
| 21 | `tmp_vchd_vt_code3` | varchar(30) | NO |
| 22 | `tmp_vchd_vt_name3` | varchar(255) | NO |
| 23 | `tmp_vchd_vt_code4` | varchar(30) | NO |
| 24 | `tmp_vchd_vt_name4` | varchar(255) | NO |
| 25 | `tmp_vchd_due` | bit | NO |
| 26 | `tmp_vchd_checked` | bit | NO |
| 27 | `tmp_vchd_autochk` | bit | NO |
| 28 | `tmp_vchd_settle` | varchar(30) | NO |
| 29 | `tmp_vchd_settle_no` | varchar(50) | NO |
| 30 | `tmp_vchd_settle_date` | datetime | YES |
| 31 | `tmp_vchd_cash_item` | varchar(30) | NO |
| 32 | `tmp_vchd_rmks` | varchar(255) | NO |
| 33 | `tmp_vchd_char1` | varchar(255) | NO |
| 34 | `tmp_vchd_char2` | varchar(255) | NO |
| 35 | `tmp_vchd_char3` | varchar(255) | NO |
| 36 | `tmp_vchd_char4` | varchar(255) | NO |
| 37 | `tmp_vchd_char5` | varchar(255) | NO |
| 38 | `tmp_vchd_char6` | varchar(255) | NO |
| 39 | `tmp_vchd_qty1` | numeric(19,8) | NO |
| 40 | `tmp_vchd_qty2` | numeric(19,8) | NO |

### `dbo.inb_hist_202512` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202601` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202602` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202603` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202604` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202605` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202606` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202607` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202608` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_202609` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inb_hist_org` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year` | int(10,0) | NO |
| 2 | `inb_month` | int(10,0) | NO |
| 3 | `inb_site` | varchar(8) | NO |
| 4 | `inb_loc` | varchar(8) | NO |
| 5 | `inb_part` | varchar(30) | NO |
| 6 | `inb_lot` | varchar(18) | NO |
| 7 | `inb_qty_beg` | numeric(19,8) | NO |
| 8 | `inb_qty_in` | numeric(19,8) | NO |
| 9 | `inb_qty_out` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_qty_adj` | numeric(19,8) | NO |
| 12 | `inb_avg_cost` | decimal(19,8) | NO |
| 13 | `inb_std_cost` | decimal(19,8) | NO |
| 14 | `inb_cost_beg` | decimal(19,8) | NO |
| 15 | `inb_cost_in` | decimal(19,8) | NO |
| 16 | `inb_cost_out` | decimal(19,8) | NO |
| 17 | `inb_cost_end` | decimal(19,8) | NO |
| 18 | `inb_cost_adj` | decimal(19,8) | NO |
| 19 | `inb_110_qty` | numeric(19,8) | NO |
| 20 | `inb_110_amt` | decimal(19,8) | NO |
| 21 | `inb_120_qty` | numeric(19,8) | NO |
| 22 | `inb_120_amt` | decimal(19,8) | NO |
| 23 | `inb_121_qty` | numeric(19,8) | NO |
| 24 | `inb_121_amt` | decimal(19,8) | NO |
| 25 | `inb_130_qty` | numeric(19,8) | NO |
| 26 | `inb_130_amt` | decimal(19,8) | NO |
| 27 | `inb_131_qty` | numeric(19,8) | NO |
| 28 | `inb_131_amt` | decimal(19,8) | NO |
| 29 | `inb_132_qty` | numeric(19,8) | NO |
| 30 | `inb_132_amt` | decimal(19,8) | NO |
| 31 | `inb_140_qty` | numeric(19,8) | NO |
| 32 | `inb_140_amt` | decimal(19,8) | NO |
| 33 | `inb_150_qty` | numeric(19,8) | NO |
| 34 | `inb_150_amt` | decimal(19,8) | NO |
| 35 | `inb_160_qty` | numeric(19,8) | NO |
| 36 | `inb_160_amt` | decimal(19,8) | NO |
| 37 | `inb_170_qty` | numeric(19,8) | NO |
| 38 | `inb_170_amt` | decimal(19,8) | NO |
| 39 | `inb_210_qty` | numeric(19,8) | NO |
| 40 | `inb_210_amt` | decimal(19,8) | NO |
| 41 | `inb_220_qty` | numeric(19,8) | NO |
| 42 | `inb_220_amt` | decimal(19,8) | NO |
| 43 | `inb_221_qty` | numeric(19,8) | NO |
| 44 | `inb_221_amt` | decimal(19,8) | NO |
| 45 | `inb_230_qty` | numeric(19,8) | NO |
| 46 | `inb_230_amt` | decimal(19,8) | NO |
| 47 | `inb_231_qty` | numeric(19,8) | NO |
| 48 | `inb_231_amt` | decimal(19,8) | NO |
| 49 | `inb_240_qty` | numeric(19,8) | NO |
| 50 | `inb_240_amt` | decimal(19,8) | NO |
| 51 | `inb_250_qty` | numeric(19,8) | NO |
| 52 | `inb_250_amt` | decimal(19,8) | NO |
| 53 | `inb_260_qty` | numeric(19,8) | NO |
| 54 | `inb_260_amt` | decimal(19,8) | NO |
| 55 | `inb_261_qty` | numeric(19,8) | NO |
| 56 | `inb_261_amt` | decimal(19,8) | NO |
| 57 | `inb_270_qty` | numeric(19,8) | NO |
| 58 | `inb_270_amt` | decimal(19,8) | NO |
| 59 | `inb_310_qty` | numeric(19,8) | NO |
| 60 | `inb_310_amt` | decimal(19,8) | NO |
| 61 | `inb_501_amt` | decimal(19,8) | NO |
| 62 | `inb_beg_mtl` | decimal(19,8) | NO |
| 63 | `inb_beg_lbr` | decimal(19,8) | NO |
| 64 | `inb_beg_bdn` | decimal(19,8) | NO |
| 65 | `inb_beg_sub` | decimal(19,8) | NO |
| 66 | `inb_beg_mtl_ll` | decimal(19,8) | NO |
| 67 | `inb_beg_lbr_ll` | decimal(19,8) | NO |
| 68 | `inb_beg_bdn_ll` | decimal(19,8) | NO |
| 69 | `inb_beg_sub_ll` | decimal(19,8) | NO |
| 70 | `inb_end_mtl` | decimal(19,8) | NO |
| 71 | `inb_end_lbr` | decimal(19,8) | NO |
| 72 | `inb_end_bdn` | decimal(19,8) | NO |
| 73 | `inb_end_sub` | decimal(19,8) | NO |
| 74 | `inb_end_mtl_ll` | decimal(19,8) | NO |
| 75 | `inb_end_lbr_ll` | decimal(19,8) | NO |
| 76 | `inb_end_bdn_ll` | decimal(19,8) | NO |
| 77 | `inb_end_sub_ll` | decimal(19,8) | NO |
| 78 | `inb_std_mtl` | decimal(19,8) | NO |
| 79 | `inb_std_lbr` | decimal(19,8) | NO |
| 80 | `inb_std_bdn` | decimal(19,8) | NO |
| 81 | `inb_std_sub` | decimal(19,8) | NO |
| 82 | `inb_std_mtl_ll` | decimal(19,8) | NO |
| 83 | `inb_std_lbr_ll` | decimal(19,8) | NO |
| 84 | `inb_std_bdn_ll` | decimal(19,8) | NO |
| 85 | `inb_std_sub_ll` | decimal(19,8) | NO |
| 86 | `inb_char1` | varchar(255) | NO |
| 87 | `inb_char2` | varchar(255) | NO |
| 88 | `inb_char3` | varchar(255) | NO |
| 89 | `inb_char4` | varchar(255) | NO |
| 90 | `inb_char5` | varchar(255) | NO |
| 91 | `inb_char6` | varchar(255) | NO |
| 92 | `inb_qty1` | decimal(19,8) | NO |
| 93 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.inv_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inv_nbr` | varchar(15) | NO |
| 2 | `inv_cust` | varchar(8) | NO |
| 3 | `inv_eff_date` | datetime | NO |
| 4 | `inv_due_date` | datetime | NO |
| 5 | `inv_disc_date` | datetime | NO |
| 6 | `inv_cr_terms` | varchar(10) | NO |
| 7 | `inv_disc` | decimal(19,8) | NO |
| 8 | `inv_vat` | decimal(19,8) | NO |
| 9 | `inv_curr` | varchar(4) | NO |
| 10 | `inv_rmks` | varchar(255) | NO |
| 11 | `inv_site` | varchar(8) | NO |
| 12 | `inv_prog_code` | varchar(12) | NO |
| 13 | `inv_crt_by` | varchar(12) | NO |
| 14 | `inv_crt_date` | datetime | NO |
| 15 | `inv_mod_times` | int(10,0) | NO |
| 16 | `inv_mod_by` | varchar(12) | NO |
| 17 | `inv_mod_date` | datetime | NO |
| 18 | `inv_pst` | bit | NO |
| 19 | `inv_pst_by` | varchar(12) | NO |
| 20 | `inv_pst_date` | datetime | YES |
| 21 | `inv_char1` | varchar(255) | NO |
| 22 | `inv_char2` | varchar(255) | NO |
| 23 | `inv_char3` | varchar(255) | NO |
| 24 | `inv_char4` | varchar(255) | NO |
| 25 | `inv_char5` | varchar(255) | NO |
| 26 | `inv_char6` | varchar(255) | NO |
| 27 | `inv_qty1` | decimal(19,8) | NO |
| 28 | `inv_qty2` | decimal(19,8) | NO |
| 29 | `inv_qty_tot` | numeric(19,8) | NO |
| 30 | `inv_amt_tot` | numeric(19,8) | NO |
| 31 | `inv_amt_ex` | numeric(19,8) | NO |
| 32 | `inv_amt_tax` | numeric(19,8) | NO |
| 33 | `inv_vo_nbr` | varchar(15) | NO |
| 34 | `inv_crt_name` | varchar(30) | NO |
| 35 | `inv_mod_name` | varchar(30) | NO |
| 36 | `inv_pst_name` | varchar(30) | NO |

### `dbo.invim_import` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `invim_seq` | int(10,0) | NO |
| 2 | `invim_date` | datetime | YES |
| 3 | `invim_cust` | varchar(8) | NO |
| 4 | `invim_so_po` | varchar(255) | NO |
| 5 | `invim_cust_part` | varchar(30) | NO |
| 6 | `invim_qty` | numeric(19,8) | NO |
| 7 | `invim_vat` | numeric(19,8) | NO |
| 8 | `invim_cost` | numeric(19,8) | NO |
| 9 | `invim_crt_by` | varchar(12) | NO |
| 10 | `invim_crt_date` | datetime | NO |
| 11 | `invim_pst` | bit | NO |
| 12 | `invim_pst_by` | varchar(12) | NO |
| 13 | `invim_pst_date` | datetime | YES |
| 14 | `invim_type` | varchar(1) | NO |
| 15 | `invim_sdh_type` | varchar(1) | NO |

### `dbo.iqc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `iqc_iqc` | varchar(15) | NO |
| 2 | `iqc_date` | datetime | NO |
| 3 | `iqc_loc_rtv` | varchar(8) | NO |
| 4 | `iqc_loc_raw` | varchar(8) | NO |
| 5 | `iqc_rmks` | varchar(255) | NO |
| 6 | `iqc_wf_status` | varchar(1) | NO |
| 7 | `iqc_site` | varchar(8) | NO |
| 8 | `iqc_prog_code` | varchar(12) | NO |
| 9 | `iqc_doc_code` | varchar(12) | NO |
| 10 | `iqc_crt_by` | varchar(12) | NO |
| 11 | `iqc_crt_date` | datetime | NO |
| 12 | `iqc_mod_times` | int(10,0) | NO |
| 13 | `iqc_mod_by` | varchar(12) | NO |
| 14 | `iqc_mod_date` | datetime | NO |
| 15 | `iqc_pst` | bit | NO |
| 16 | `iqc_pst_by` | varchar(12) | NO |
| 17 | `iqc_pst_date` | datetime | YES |
| 18 | `iqc_char1` | varchar(255) | NO |
| 19 | `iqc_char2` | varchar(255) | NO |
| 20 | `iqc_char3` | varchar(255) | NO |
| 21 | `iqc_char4` | varchar(255) | NO |
| 22 | `iqc_char5` | varchar(255) | NO |
| 23 | `iqc_char6` | varchar(255) | NO |
| 24 | `iqc_qty1` | decimal(19,8) | NO |
| 25 | `iqc_qty2` | decimal(19,8) | NO |
| 26 | `iqc_chk` | bit | NO |
| 27 | `iqc_chk_by` | varchar(12) | NO |
| 28 | `iqc_chk_date` | datetime | YES |
| 29 | `iqc_data_src` | varchar(1) | NO |
| 30 | `iqc_data_id` | varchar(255) | NO |

### `dbo.iqcd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `iqcd_iqc` | varchar(15) | NO |
| 2 | `iqcd_line` | int(10,0) | NO |
| 3 | `iqcd_grn` | varchar(15) | NO |
| 4 | `iqcd_grn_line` | int(10,0) | NO |
| 5 | `iqcd_po` | varchar(15) | NO |
| 6 | `iqcd_po_line` | int(10,0) | NO |
| 7 | `iqcd_part` | varchar(30) | NO |
| 8 | `iqcd_qty_pending` | numeric(19,8) | NO |
| 9 | `iqcd_qty_acpt` | numeric(19,8) | NO |
| 10 | `iqcd_qty_rts` | numeric(19,8) | NO |
| 11 | `iqcd_site` | varchar(8) | NO |
| 12 | `iqcd_loc_iqc` | varchar(8) | NO |
| 13 | `iqcd_loc_raw` | varchar(8) | NO |
| 14 | `iqcd_loc_rtv` | varchar(8) | NO |
| 15 | `iqcd_lot` | varchar(18) | NO |
| 16 | `iqcd_um` | varchar(4) | NO |
| 17 | `iqcd_um_rate_m` | decimal(19,8) | NO |
| 18 | `iqcd_um_rate_d` | decimal(19,8) | NO |
| 19 | `iqcd_grade` | varchar(2) | NO |
| 20 | `iqcd_rmks` | varchar(255) | NO |
| 21 | `iqcd_type` | varchar(1) | NO |
| 22 | `iqcd_wt` | decimal(19,8) | NO |
| 23 | `iqcd_price` | numeric(19,8) | NO |
| 24 | `iqcd_deduction` | decimal(19,8) | NO |
| 25 | `iqcd_crt_by` | varchar(12) | NO |
| 26 | `iqcd_crt_date` | datetime | NO |
| 27 | `iqcd_mod_times` | int(10,0) | NO |
| 28 | `iqcd_mod_by` | varchar(12) | NO |
| 29 | `iqcd_mod_date` | datetime | NO |
| 30 | `iqcd_char1` | varchar(255) | NO |
| 31 | `iqcd_char2` | varchar(255) | NO |
| 32 | `iqcd_char3` | varchar(255) | NO |
| 33 | `iqcd_char4` | varchar(255) | NO |
| 34 | `iqcd_char5` | varchar(255) | NO |
| 35 | `iqcd_char6` | varchar(255) | NO |
| 36 | `iqcd_qty1` | decimal(19,8) | NO |
| 37 | `iqcd_qty2` | decimal(19,8) | NO |
| 38 | `iqcd_qty_pending_inv` | numeric(19,8) | NO |
| 39 | `iqcd_qty_acpt_inv` | numeric(19,8) | NO |
| 40 | `iqcd_qty_rts_inv` | numeric(19,8) | NO |
| 41 | `iqcd_data_src` | varchar(1) | NO |
| 42 | `iqcd_data_id` | varchar(255) | NO |

### `dbo.itf_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `itf_lang` | varchar(3) | NO |
| 2 | `itf_prog_code` | varchar(12) | NO |
| 3 | `itf_table` | varchar(30) | NO |
| 4 | `itf_field` | varchar(30) | NO |
| 5 | `itf_ctrl_name` | varchar(255) | NO |
| 6 | `itf_ctrl_left` | int(10,0) | NO |
| 7 | `itf_ctrl_top` | int(10,0) | NO |
| 8 | `itf_ctrl_width` | int(10,0) | NO |
| 9 | `itf_ctrl_height` | int(10,0) | NO |
| 10 | `itf_cn_caption` | varchar(255) | NO |
| 11 | `itf_lang_caption` | varchar(255) | NO |
| 12 | `itf_crt_by` | varchar(12) | NO |
| 13 | `itf_crt_date` | datetime | NO |
| 14 | `itf_mod_times` | int(10,0) | NO |
| 15 | `itf_mod_by` | varchar(12) | NO |
| 16 | `itf_mod_date` | datetime | NO |
| 17 | `itf_char1` | varchar(255) | NO |
| 18 | `itf_char2` | varchar(255) | NO |
| 19 | `itf_char3` | varchar(255) | NO |
| 20 | `itf_char4` | varchar(255) | NO |
| 21 | `itf_char5` | varchar(255) | NO |
| 22 | `itf_char6` | varchar(255) | NO |
| 23 | `itf_qty1` | decimal(19,8) | NO |
| 24 | `itf_qty2` | decimal(19,8) | NO |

### `dbo.kpi_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `kpi_code` | varchar(15) | NO |
| 2 | `kpi_dept` | varchar(10) | NO |
| 3 | `kpi_name` | varchar(50) | NO |
| 4 | `kpi_std_desc` | varchar(255) | NO |
| 5 | `kpi_rmks` | varchar(255) | NO |
| 6 | `kpi_src` | varchar(1) | NO |
| 7 | `kpi_aim` | numeric(19,8) | NO |
| 8 | `kpi_formula` | varchar(8000) | NO |
| 9 | `kpi_score` | numeric(19,8) | NO |
| 10 | `kpi_score_fm` | varchar(4000) | NO |
| 11 | `kpi_start` | datetime | NO |
| 12 | `kpi_expire` | datetime | NO |
| 13 | `kpi_crt_by` | varchar(12) | NO |
| 14 | `kpi_crt_date` | datetime | NO |
| 15 | `kpi_mod_times` | int(10,0) | NO |
| 16 | `kpi_mod_by` | varchar(12) | NO |
| 17 | `kpi_mod_date` | datetime | NO |
| 18 | `kpi_pst` | bit | NO |
| 19 | `kpi_pst_by` | varchar(12) | NO |
| 20 | `kpi_pst_date` | datetime | YES |
| 21 | `kpi_char1` | varchar(255) | NO |
| 22 | `kpi_char2` | varchar(255) | NO |
| 23 | `kpi_char3` | varchar(255) | NO |
| 24 | `kpi_char4` | varchar(255) | NO |
| 25 | `kpi_char5` | varchar(255) | NO |
| 26 | `kpi_char6` | varchar(255) | NO |
| 27 | `kpi_qty1` | decimal(19,8) | NO |
| 28 | `kpi_qty2` | decimal(19,8) | NO |

### `dbo.kpt_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `kpt_user` | varchar(12) | NO |
| 2 | `kpt_dept` | varchar(10) | NO |
| 3 | `kpt_filename` | varchar(255) | NO |
| 4 | `kpt_visible` | bit | NO |
| 5 | `kpt_char1` | varchar(255) | NO |
| 6 | `kpt_char2` | varchar(255) | NO |
| 7 | `kpt_char3` | varchar(255) | NO |
| 8 | `kpt_char4` | varchar(255) | NO |
| 9 | `kpt_char5` | varchar(255) | NO |
| 10 | `kpt_char6` | varchar(255) | NO |
| 11 | `kpt_qty1` | decimal(19,8) | NO |
| 12 | `kpt_qty2` | decimal(19,8) | NO |

### `dbo.ld_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ld_site` | varchar(8) | NO |
| 2 | `ld_loc` | varchar(8) | NO |
| 3 | `ld_part` | varchar(30) | NO |
| 4 | `ld_lot` | varchar(18) | NO |
| 5 | `ld_qty_oh` | numeric(19,8) | NO |
| 6 | `ld_date` | datetime | NO |
| 7 | `ld_grade` | varchar(2) | NO |
| 8 | `ld_char1` | varchar(255) | NO |
| 9 | `ld_char2` | varchar(255) | NO |
| 10 | `ld_char3` | varchar(255) | NO |
| 11 | `ld_char4` | varchar(255) | NO |
| 12 | `ld_char5` | varchar(255) | NO |
| 13 | `ld_char6` | varchar(255) | NO |
| 14 | `ld_qty1` | decimal(19,8) | NO |
| 15 | `ld_qty2` | decimal(19,8) | NO |
| 16 | `ld_loc_pos` | varchar(18) | NO |

### `dbo.ldp_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ldp_site` | varchar(8) | NO |
| 2 | `ldp_loc` | varchar(8) | NO |
| 3 | `ldp_part` | varchar(30) | NO |
| 4 | `ldp_lot` | varchar(18) | NO |
| 5 | `ldp_pos` | varchar(30) | NO |
| 6 | `ldp_qty` | numeric(19,8) | NO |
| 7 | `ldp_date` | datetime | NO |
| 8 | `ldp_char1` | varchar(255) | NO |
| 9 | `ldp_char2` | varchar(255) | NO |
| 10 | `ldp_char3` | varchar(255) | NO |
| 11 | `ldp_char4` | varchar(255) | NO |
| 12 | `ldp_char5` | varchar(255) | NO |
| 13 | `ldp_char6` | varchar(255) | NO |
| 14 | `ldp_qty1` | decimal(19,8) | NO |
| 15 | `ldp_qty2` | decimal(19,8) | NO |

### `dbo.ln_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ln_site` | varchar(8) | NO |
| 2 | `ln_line` | varchar(8) | NO |
| 3 | `ln_desc` | varchar(50) | NO |
| 4 | `ln_loc_ovr` | varchar(8) | NO |
| 5 | `ln_crt_by` | varchar(12) | NO |
| 6 | `ln_crt_date` | datetime | NO |
| 7 | `ln_char1` | varchar(255) | NO |
| 8 | `ln_char2` | varchar(255) | NO |
| 9 | `ln_char3` | varchar(255) | NO |
| 10 | `ln_char4` | varchar(255) | NO |
| 11 | `ln_char5` | varchar(255) | NO |
| 12 | `ln_char6` | varchar(255) | NO |
| 13 | `ln_qty1` | decimal(19,8) | NO |
| 14 | `ln_qty2` | decimal(19,8) | NO |

### `dbo.loc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `loc_site` | varchar(8) | NO |
| 2 | `loc_loc` | varchar(8) | NO |
| 3 | `loc_desc` | varchar(30) | NO |
| 4 | `loc_type` | varchar(8) | NO |
| 5 | `loc_nettable` | bit | NO |
| 6 | `loc_avail` | bit | NO |
| 7 | `loc_overissue` | bit | NO |
| 8 | `loc_disabled` | bit | NO |
| 9 | `loc_keeper` | varchar(12) | NO |
| 10 | `loc_perm` | varchar(80) | NO |
| 11 | `loc_crt_by` | varchar(12) | NO |
| 12 | `loc_crt_date` | datetime | NO |
| 13 | `loc_mod_times` | int(10,0) | NO |
| 14 | `loc_mod_by` | varchar(12) | NO |
| 15 | `loc_mod_date` | datetime | NO |
| 16 | `loc_ac_code_inv` | varchar(15) | NO |
| 17 | `loc_ac_code_sls` | varchar(15) | NO |
| 18 | `loc_char1` | varchar(255) | NO |
| 19 | `loc_char2` | varchar(255) | NO |
| 20 | `loc_char3` | varchar(255) | NO |
| 21 | `loc_char4` | varchar(255) | NO |
| 22 | `loc_char5` | varchar(255) | NO |
| 23 | `loc_char6` | varchar(255) | NO |
| 24 | `loc_qty1` | decimal(19,8) | NO |
| 25 | `loc_qty2` | decimal(19,8) | NO |
| 26 | `loc_rtn_nocharge` | bit | NO |
| 27 | `loc_ac_code_shipped` | varchar(15) | NO |
| 28 | `loc_ac_code_scost` | varchar(15) | NO |
| 29 | `loc_ac_code_wcost` | varchar(15) | NO |
| 30 | `loc_ac_code_comm` | varchar(15) | NO |
| 31 | `loc_crt_name` | varchar(30) | NO |
| 32 | `loc_mod_name` | varchar(30) | NO |

### `dbo.log_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `log_seq` | int(10,0) | NO |
| 2 | `log_part` | varchar(30) | NO |
| 3 | `log_db` | varchar(30) | NO |
| 4 | `log_sync_old` | bit | NO |
| 5 | `log_sync_new` | bit | NO |
| 6 | `log_change_by` | varchar(12) | NO |
| 7 | `log_change_date` | datetime | NO |

### `dbo.lotd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `lotd_flow` | int(10,0) | NO |
| 2 | `lotd_part` | varchar(30) | NO |
| 3 | `lotd_lot` | varchar(50) | NO |
| 4 | `lotd_effdate` | datetime | NO |
| 5 | `lotd_ref` | varchar(15) | NO |
| 6 | `lotd_ref_line` | int(10,0) | NO |
| 7 | `lotd_prop1` | varchar(50) | NO |
| 8 | `lotd_prop2` | varchar(50) | NO |
| 9 | `lotd_prop3` | varchar(50) | NO |
| 10 | `lotd_prop4` | varchar(50) | NO |
| 11 | `lotd_prop5` | varchar(50) | NO |
| 12 | `lotd_prop6` | varchar(255) | NO |
| 13 | `lotd_prop7` | varchar(255) | NO |
| 14 | `lotd_prop8` | varchar(255) | NO |
| 15 | `lotd_prop9` | varchar(255) | NO |
| 16 | `lotd_rmks` | varchar(255) | NO |
| 17 | `lotd_used` | bit | NO |
| 18 | `lotd_crt_by` | varchar(12) | NO |
| 19 | `lotd_crt_date` | datetime | NO |

### `dbo.lp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `lp_nbr` | varchar(15) | NO |
| 2 | `lp_date` | datetime | NO |
| 3 | `lp_type` | varchar(1) | NO |
| 4 | `lp_src` | varchar(8) | NO |
| 5 | `lp_src_nbr` | varchar(15) | NO |
| 6 | `lp_rmks` | varchar(255) | NO |
| 7 | `lp_prog_code` | varchar(255) | NO |
| 8 | `lp_site` | varchar(8) | NO |
| 9 | `lp_crt_by` | varchar(12) | NO |
| 10 | `lp_crt_date` | datetime | NO |
| 11 | `lp_mod_times` | int(10,0) | NO |
| 12 | `lp_mod_by` | varchar(12) | NO |
| 13 | `lp_mod_date` | datetime | NO |
| 14 | `lp_pst` | bit | NO |
| 15 | `lp_pst_by` | varchar(12) | NO |
| 16 | `lp_pst_date` | datetime | YES |
| 17 | `lp_data_src` | varchar(1) | NO |
| 18 | `lp_data_id` | varchar(255) | NO |
| 19 | `lp_char1` | varchar(255) | NO |
| 20 | `lp_char2` | varchar(255) | NO |
| 21 | `lp_char3` | varchar(255) | NO |
| 22 | `lp_char4` | varchar(255) | NO |
| 23 | `lp_char5` | varchar(255) | NO |
| 24 | `lp_char6` | varchar(255) | NO |
| 25 | `lp_qty1` | decimal(19,8) | NO |
| 26 | `lp_qty2` | decimal(19,8) | NO |

### `dbo.lpd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `lpd_nbr` | varchar(15) | NO |
| 2 | `lpd_line` | int(10,0) | NO |
| 3 | `lpd_date` | datetime | NO |
| 4 | `lpd_src` | varchar(8) | NO |
| 5 | `lpd_src_nbr` | varchar(15) | NO |
| 6 | `lpd_src_line` | int(10,0) | NO |
| 7 | `lpd_part` | varchar(30) | NO |
| 8 | `lpd_lot` | varchar(18) | NO |
| 9 | `lpd_loc_fr` | varchar(8) | NO |
| 10 | `lpd_pos_fr` | varchar(30) | NO |
| 11 | `lpd_loc_to` | varchar(8) | NO |
| 12 | `lpd_pos_to` | varchar(30) | NO |
| 13 | `lpd_qty` | numeric(19,8) | NO |
| 14 | `lpd_barcode` | varchar(1000) | YES |
| 15 | `lpd_rmks` | varchar(255) | NO |
| 16 | `lpd_crt_by` | varchar(12) | NO |
| 17 | `lpd_crt_date` | datetime | NO |
| 18 | `lpd_mod_times` | int(10,0) | NO |
| 19 | `lpd_mod_by` | varchar(12) | NO |
| 20 | `lpd_mod_date` | datetime | NO |
| 21 | `lpd_data_src` | varchar(1) | NO |
| 22 | `lpd_data_id` | varchar(255) | NO |
| 23 | `lpd_char1` | varchar(255) | NO |
| 24 | `lpd_char2` | varchar(255) | NO |
| 25 | `lpd_char3` | varchar(255) | NO |
| 26 | `lpd_char4` | varchar(255) | NO |
| 27 | `lpd_char5` | varchar(255) | NO |
| 28 | `lpd_char6` | varchar(255) | NO |
| 29 | `lpd_qty1` | decimal(19,8) | NO |
| 30 | `lpd_qty2` | decimal(19,8) | NO |

### `dbo.mnd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mnd_lang` | varchar(3) | NO |
| 2 | `mnd_par` | varchar(30) | NO |
| 3 | `mnd_select` | int(10,0) | NO |
| 4 | `mnd_rpt` | varchar(30) | NO |
| 5 | `mnd_desc` | varchar(255) | NO |
| 6 | `mnd_perm` | varchar(255) | NO |
| 7 | `mnd_disable` | bit | NO |
| 8 | `mnd_crt_by` | varchar(12) | NO |
| 9 | `mnd_crt_date` | datetime | NO |
| 10 | `mnd_char1` | varchar(255) | NO |
| 11 | `mnd_char2` | varchar(255) | NO |
| 12 | `mnd_char3` | varchar(255) | NO |
| 13 | `mnd_char4` | varchar(255) | NO |
| 14 | `mnd_char5` | varchar(255) | NO |
| 15 | `mnd_char6` | varchar(255) | NO |
| 16 | `mnd_qty1` | decimal(19,8) | NO |
| 17 | `mnd_qty2` | decimal(19,8) | NO |
| 18 | `mnd_pnt_times` | int(10,0) | NO |
| 19 | `mnd_pnt_perm` | varchar(255) | NO |

### `dbo.mov_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mov_mov` | varchar(15) | NO |
| 2 | `mov_date` | datetime | NO |
| 3 | `mov_cat` | varchar(30) | NO |
| 4 | `mov_dept_fr` | varchar(10) | NO |
| 5 | `mov_dept_to` | varchar(10) | NO |
| 6 | `mov_type` | varchar(8) | NO |
| 7 | `mov_site` | varchar(8) | NO |
| 8 | `mov_fr` | varchar(8) | NO |
| 9 | `mov_site2` | varchar(8) | NO |
| 10 | `mov_to` | varchar(8) | NO |
| 11 | `mov_rmks` | varchar(255) | NO |
| 12 | `mov_wf_status` | varchar(1) | NO |
| 13 | `mov_prog_code` | varchar(12) | NO |
| 14 | `mov_doc_code` | varchar(12) | NO |
| 15 | `mov_crt_by` | varchar(12) | NO |
| 16 | `mov_crt_date` | datetime | NO |
| 17 | `mov_mod_times` | int(10,0) | NO |
| 18 | `mov_mod_by` | varchar(12) | NO |
| 19 | `mov_mod_date` | datetime | NO |
| 20 | `mov_pst` | bit | NO |
| 21 | `mov_pst_by` | varchar(12) | NO |
| 22 | `mov_pst_date` | datetime | YES |
| 23 | `mov_char1` | varchar(255) | NO |
| 24 | `mov_char2` | varchar(255) | NO |
| 25 | `mov_char3` | varchar(255) | NO |
| 26 | `mov_char4` | varchar(255) | NO |
| 27 | `mov_char5` | varchar(255) | NO |
| 28 | `mov_char6` | varchar(255) | NO |
| 29 | `mov_qty1` | decimal(19,8) | NO |
| 30 | `mov_qty2` | decimal(19,8) | NO |
| 31 | `mov_data_src` | varchar(1) | NO |
| 32 | `mov_data_id` | varchar(255) | NO |
| 33 | `mov_src` | varchar(2) | NO |
| 34 | `mov_src_nbr` | varchar(15) | NO |
| 35 | `mov_src_lot` | varchar(18) | NO |
| 36 | `mov_chk` | bit | NO |
| 37 | `mov_chk_by` | varchar(12) | NO |
| 38 | `mov_chk_date` | datetime | YES |
| 39 | `mov_data_nbr` | varchar(15) | NO |
| 40 | `mov_allow` | bit | NO |
| 41 | `mov_allow_by` | varchar(12) | NO |
| 42 | `mov_allow_date` | datetime | YES |
| 43 | `mov_vd_chk` | bit | NO |
| 44 | `mov_vd_chk_by` | varchar(12) | NO |
| 45 | `mov_vd_chk_date` | datetime | YES |
| 46 | `mov_kind` | varchar(1) | NO |
| 47 | `mov_vend` | varchar(8) | NO |

### `dbo.movd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `movd_mov` | varchar(15) | NO |
| 2 | `movd_line` | int(10,0) | NO |
| 3 | `movd_part` | varchar(30) | NO |
| 4 | `movd_qty` | numeric(19,8) | NO |
| 5 | `movd_site` | varchar(8) | NO |
| 6 | `movd_fr` | varchar(8) | NO |
| 7 | `movd_site2` | varchar(8) | NO |
| 8 | `movd_to` | varchar(8) | NO |
| 9 | `movd_lot` | varchar(18) | NO |
| 10 | `movd_cost` | decimal(19,8) | NO |
| 11 | `movd_grade` | varchar(2) | NO |
| 12 | `movd_rmks` | varchar(255) | NO |
| 13 | `movd_crt_by` | varchar(12) | NO |
| 14 | `movd_crt_date` | datetime | NO |
| 15 | `movd_mod_times` | int(10,0) | NO |
| 16 | `movd_mod_by` | varchar(12) | NO |
| 17 | `movd_mod_date` | datetime | NO |
| 18 | `movd_char1` | varchar(255) | NO |
| 19 | `movd_char2` | varchar(255) | NO |
| 20 | `movd_char3` | varchar(255) | NO |
| 21 | `movd_char4` | varchar(255) | NO |
| 22 | `movd_char5` | varchar(255) | NO |
| 23 | `movd_char6` | varchar(255) | NO |
| 24 | `movd_qty1` | decimal(19,8) | NO |
| 25 | `movd_qty2` | decimal(19,8) | NO |
| 26 | `movd_src_nbr` | varchar(15) | NO |
| 27 | `movd_src_line` | int(10,0) | NO |
| 28 | `movd_qty_fini` | numeric(19,8) | NO |
| 29 | `movd_data_src` | varchar(1) | NO |
| 30 | `movd_data_id` | varchar(255) | NO |

### `dbo.mrp_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mrp_dataset` | varchar(15) | NO |
| 2 | `mrp_site` | varchar(8) | NO |
| 3 | `mrp_part` | varchar(30) | NO |
| 4 | `mrp_nbr` | varchar(18) | NO |
| 5 | `mrp_line` | varchar(18) | NO |
| 6 | `mrp_line2` | varchar(15) | NO |
| 7 | `mrp_qty` | numeric(19,8) | NO |
| 8 | `mrp_type` | varchar(8) | NO |
| 9 | `mrp_due_date` | datetime | NO |
| 10 | `mrp_rel_date` | datetime | NO |
| 11 | `mrp_detail` | varchar(255) | NO |
| 12 | `mrp_char1` | varchar(255) | NO |
| 13 | `mrp_char2` | varchar(255) | NO |
| 14 | `mrp_char3` | varchar(255) | NO |
| 15 | `mrp_char4` | varchar(255) | NO |
| 16 | `mrp_char5` | varchar(255) | NO |
| 17 | `mrp_char6` | varchar(255) | NO |
| 18 | `mrp_qty1` | decimal(19,8) | NO |
| 19 | `mrp_qty2` | decimal(19,8) | NO |

### `dbo.mrpl_log` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mrpl_log` | int(10,0) | NO |
| 2 | `mrpl_site` | varchar(8) | NO |
| 3 | `mrpl_memo` | varchar(255) | NO |
| 4 | `mrpl_time` | datetime | YES |
| 5 | `mrpl_char1` | varchar(255) | NO |
| 6 | `mrpl_char2` | varchar(255) | NO |
| 7 | `mrpl_char3` | varchar(255) | NO |
| 8 | `mrpl_char4` | varchar(255) | NO |
| 9 | `mrpl_char5` | varchar(255) | NO |
| 10 | `mrpl_char6` | varchar(255) | NO |
| 11 | `mrpl_qty1` | decimal(19,8) | NO |
| 12 | `mrpl_qty2` | decimal(19,8) | NO |

### `dbo.mstr1005` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sc_nbr` | varchar(15) | NO |
| 2 | `sc_cust` | varchar(8) | NO |
| 3 | `sc_curr` | varchar(4) | NO |
| 4 | `sc_part` | varchar(30) | NO |
| 5 | `sc_cust_part` | varchar(80) | NO |
| 6 | `sc_um` | varchar(4) | NO |
| 7 | `sc_um_rate_m` | decimal(19,8) | NO |
| 8 | `sc_um_rate_d` | decimal(19,8) | NO |
| 9 | `sc_start` | datetime | NO |
| 10 | `sc_expire` | datetime | NO |
| 11 | `sc_vat` | bit | NO |
| 12 | `sc_vat_rate` | decimal(19,8) | NO |
| 13 | `sc_disc` | decimal(19,8) | NO |
| 14 | `sc_price` | decimal(19,8) | NO |
| 15 | `sc_rmks` | varchar(255) | NO |
| 16 | `sc_crt_by` | varchar(12) | NO |
| 17 | `sc_crt_date` | datetime | NO |
| 18 | `sc_wf_status` | varchar(1) | NO |
| 19 | `sc_mod_times` | int(10,0) | NO |
| 20 | `sc_mod_by` | varchar(12) | NO |
| 21 | `sc_mod_date` | datetime | NO |
| 22 | `sc_pst` | bit | NO |
| 23 | `sc_pst_by` | varchar(12) | NO |
| 24 | `sc_pst_date` | datetime | YES |
| 25 | `sc_char1` | varchar(255) | NO |
| 26 | `sc_char2` | varchar(255) | NO |
| 27 | `sc_char3` | varchar(255) | NO |
| 28 | `sc_char4` | varchar(255) | NO |
| 29 | `sc_char5` | varchar(255) | NO |
| 30 | `sc_char6` | varchar(255) | NO |
| 31 | `sc_qty1` | decimal(19,8) | NO |
| 32 | `sc_qty2` | decimal(19,8) | NO |
| 33 | `sc_ast_code` | varchar(15) | NO |
| 34 | `sc_spare_pct` | decimal(19,8) | NO |
| 35 | `sc_data_src` | varchar(1) | NO |
| 36 | `sc_data_id` | varchar(255) | NO |
| 37 | `sc_prog_code` | varchar(12) | NO |
| 38 | `sc_qtype` | varchar(2) | NO |
| 39 | `sc_cu_area` | varchar(30) | NO |
| 40 | `sc_cu_curr` | varchar(30) | NO |
| 41 | `sc_price_type` | varchar(1) | NO |
| 42 | `sc_prop1` | varchar(30) | NO |
| 43 | `sc_prop2` | varchar(30) | NO |
| 44 | `sc_prop3` | varchar(30) | NO |
| 45 | `sc_prop4` | varchar(30) | NO |
| 46 | `sc_chk` | bit | NO |
| 47 | `sc_chk_by` | varchar(12) | NO |
| 48 | `sc_chk_date` | datetime | YES |
| 49 | `sc_appro` | bit | NO |
| 50 | `sc_appro_by` | varchar(12) | NO |
| 51 | `sc_appro_date` | datetime | YES |

### `dbo.mtr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mtr_mtr` | varchar(15) | NO |
| 2 | `mtr_date` | datetime | NO |
| 3 | `mtr_nbr` | varchar(15) | NO |
| 4 | `mtr_lot` | varchar(18) | NO |
| 5 | `mtr_rmks` | varchar(255) | NO |
| 6 | `mtr_wf_status` | varchar(1) | NO |
| 7 | `mtr_site` | varchar(8) | NO |
| 8 | `mtr_prog_code` | varchar(12) | NO |
| 9 | `mtr_doc_code` | varchar(12) | NO |
| 10 | `mtr_crt_by` | varchar(12) | NO |
| 11 | `mtr_crt_date` | datetime | NO |
| 12 | `mtr_mod_times` | int(10,0) | NO |
| 13 | `mtr_mod_by` | varchar(12) | NO |
| 14 | `mtr_mod_date` | datetime | NO |
| 15 | `mtr_pst` | bit | NO |
| 16 | `mtr_pst_by` | varchar(12) | NO |
| 17 | `mtr_pst_date` | datetime | YES |
| 18 | `mtr_char1` | varchar(255) | NO |
| 19 | `mtr_char2` | varchar(255) | NO |
| 20 | `mtr_char3` | varchar(255) | NO |
| 21 | `mtr_char4` | varchar(255) | NO |
| 22 | `mtr_char5` | varchar(255) | NO |
| 23 | `mtr_char6` | varchar(255) | NO |
| 24 | `mtr_qty1` | decimal(19,8) | NO |
| 25 | `mtr_qty2` | decimal(19,8) | NO |
| 26 | `mtr_data_src` | varchar(1) | NO |
| 27 | `mtr_data_id` | varchar(255) | NO |
| 28 | `mtr_data_nbr` | varchar(255) | NO |

### `dbo.mtrd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mtrd_mtr` | varchar(15) | NO |
| 2 | `mtrd_line` | int(10,0) | NO |
| 3 | `mtrd_wo_nbr` | varchar(15) | NO |
| 4 | `mtrd_wo_lot` | varchar(18) | NO |
| 5 | `mtrd_seq` | int(10,0) | NO |
| 6 | `mtrd_seq2` | int(10,0) | NO |
| 7 | `mtrd_type` | varchar(1) | NO |
| 8 | `mtrd_part` | varchar(30) | NO |
| 9 | `mtrd_site` | varchar(8) | NO |
| 10 | `mtrd_loc` | varchar(8) | NO |
| 11 | `mtrd_lot` | varchar(18) | NO |
| 12 | `mtrd_qty` | numeric(19,8) | NO |
| 13 | `mtrd_op` | int(10,0) | NO |
| 14 | `mtrd_rmks` | varchar(255) | NO |
| 15 | `mtrd_crt_by` | varchar(12) | NO |
| 16 | `mtrd_crt_date` | datetime | NO |
| 17 | `mtrd_mod_times` | int(10,0) | NO |
| 18 | `mtrd_mod_by` | varchar(12) | NO |
| 19 | `mtrd_mod_date` | datetime | NO |
| 20 | `mtrd_char1` | varchar(255) | NO |
| 21 | `mtrd_char2` | varchar(255) | NO |
| 22 | `mtrd_char3` | varchar(255) | NO |
| 23 | `mtrd_char4` | varchar(255) | NO |
| 24 | `mtrd_char5` | varchar(255) | NO |
| 25 | `mtrd_char6` | varchar(255) | NO |
| 26 | `mtrd_qty1` | decimal(19,8) | NO |
| 27 | `mtrd_qty2` | decimal(19,8) | NO |
| 28 | `mtrd_data_src` | varchar(1) | NO |
| 29 | `mtrd_data_id` | varchar(255) | NO |

### `dbo.mts_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mts_mts` | varchar(15) | NO |
| 2 | `mts_date` | datetime | NO |
| 3 | `mts_nbr` | varchar(15) | NO |
| 4 | `mts_lot` | varchar(18) | NO |
| 5 | `mts_rmks` | varchar(255) | NO |
| 6 | `mts_wf_status` | varchar(1) | NO |
| 7 | `mts_site` | varchar(8) | NO |
| 8 | `mts_prog_code` | varchar(12) | NO |
| 9 | `mts_doc_code` | varchar(12) | NO |
| 10 | `mts_crt_by` | varchar(12) | NO |
| 11 | `mts_crt_date` | datetime | NO |
| 12 | `mts_mod_times` | int(10,0) | NO |
| 13 | `mts_mod_by` | varchar(12) | NO |
| 14 | `mts_mod_date` | datetime | NO |
| 15 | `mts_pst` | bit | NO |
| 16 | `mts_pst_by` | varchar(12) | NO |
| 17 | `mts_pst_date` | datetime | YES |
| 18 | `mts_char1` | varchar(255) | NO |
| 19 | `mts_char2` | varchar(255) | NO |
| 20 | `mts_char3` | varchar(255) | NO |
| 21 | `mts_char4` | varchar(255) | NO |
| 22 | `mts_char5` | varchar(255) | NO |
| 23 | `mts_char6` | varchar(255) | NO |
| 24 | `mts_qty1` | decimal(19,8) | NO |
| 25 | `mts_qty2` | decimal(19,8) | NO |

### `dbo.mtsd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `mtsd_mts` | varchar(15) | NO |
| 2 | `mtsd_line` | int(10,0) | NO |
| 3 | `mtsd_wo_nbr` | varchar(15) | NO |
| 4 | `mtsd_wo_lot` | varchar(18) | NO |
| 5 | `mtsd_seq` | int(10,0) | NO |
| 6 | `mtsd_part` | varchar(30) | NO |
| 7 | `mtsd_qty_scr` | numeric(19,8) | NO |
| 8 | `mtsd_rmks` | varchar(255) | NO |
| 9 | `mtsd_crt_by` | varchar(12) | NO |
| 10 | `mtsd_crt_date` | datetime | NO |
| 11 | `mtsd_mod_times` | int(10,0) | NO |
| 12 | `mtsd_mod_by` | varchar(12) | NO |
| 13 | `mtsd_mod_date` | datetime | NO |
| 14 | `mtsd_char1` | varchar(255) | NO |
| 15 | `mtsd_char2` | varchar(255) | NO |
| 16 | `mtsd_char3` | varchar(255) | NO |
| 17 | `mtsd_char4` | varchar(255) | NO |
| 18 | `mtsd_char5` | varchar(255) | NO |
| 19 | `mtsd_char6` | varchar(255) | NO |
| 20 | `mtsd_qty1` | decimal(19,8) | NO |
| 21 | `mtsd_qty2` | decimal(19,8) | NO |

### `dbo.new_table_name925BAK` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cp_cust` | varchar(8) | NO |
| 2 | `cp_part` | varchar(30) | NO |
| 3 | `cp_cust_part` | varchar(80) | NO |
| 4 | `cp_cust_desc` | varchar(255) | NO |
| 5 | `cp_um` | varchar(4) | NO |
| 6 | `cp_um_rate_m` | decimal(19,8) | NO |
| 7 | `cp_um_rate_d` | decimal(19,8) | NO |
| 8 | `cp_cmmt` | varchar(255) | NO |
| 9 | `cp_crt_by` | varchar(12) | NO |
| 10 | `cp_crt_date` | datetime | NO |
| 11 | `cp_char1` | varchar(255) | NO |
| 12 | `cp_char2` | varchar(255) | NO |
| 13 | `cp_char3` | varchar(255) | NO |
| 14 | `cp_char4` | varchar(255) | NO |
| 15 | `cp_char5` | varchar(255) | NO |
| 16 | `cp_char6` | varchar(255) | NO |
| 17 | `cp_qty1` | decimal(19,8) | NO |
| 18 | `cp_qty2` | decimal(19,8) | NO |

### `dbo.oa_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `oa_flow_no` | int(10,0) | NO |
| 2 | `oa_site` | varchar(8) | NO |
| 3 | `oa_part` | varchar(30) | NO |
| 4 | `oa_code` | int(10,0) | NO |
| 5 | `oa_nbr` | varchar(18) | NO |
| 6 | `oa_line` | varchar(18) | NO |
| 7 | `oa_to_date` | datetime | NO |
| 8 | `oa_fr_date` | datetime | YES |
| 9 | `oa_detail` | varchar(255) | NO |
| 10 | `oa_qty` | numeric(19,8) | NO |
| 11 | `oa_char1` | varchar(255) | NO |
| 12 | `oa_char2` | varchar(255) | NO |
| 13 | `oa_char3` | varchar(255) | NO |
| 14 | `oa_char4` | varchar(255) | NO |
| 15 | `oa_char5` | varchar(255) | NO |
| 16 | `oa_char6` | varchar(255) | NO |
| 17 | `oa_qty1` | decimal(19,8) | NO |
| 18 | `oa_qty2` | decimal(19,8) | NO |

### `dbo.opd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `opd_company` | varchar(8) | NO |
| 2 | `opd_line` | int(10,0) | NO |
| 3 | `opd_ac_code` | varchar(15) | NO |
| 4 | `opd_curr` | varchar(4) | NO |
| 5 | `opd_ex_rate` | decimal(19,8) | NO |
| 6 | `opd_d_qty` | numeric(19,8) | NO |
| 7 | `opd_d_amt` | numeric(19,8) | NO |
| 8 | `opd_d_amt_base` | numeric(19,8) | NO |
| 9 | `opd_c_qty` | numeric(19,8) | NO |
| 10 | `opd_c_amt` | numeric(19,8) | NO |
| 11 | `opd_c_amt_base` | numeric(19,8) | NO |
| 12 | `opd_id_qty` | numeric(19,8) | NO |
| 13 | `opd_id_amt` | numeric(19,8) | NO |
| 14 | `opd_id_amt_base` | numeric(19,8) | NO |
| 15 | `opd_ic_qty` | numeric(19,8) | NO |
| 16 | `opd_ic_amt` | numeric(19,8) | NO |
| 17 | `opd_ic_amt_base` | numeric(19,8) | NO |
| 18 | `opd_use_ai` | bit | NO |
| 19 | `opd_crt_by` | varchar(12) | NO |
| 20 | `opd_crt_date` | datetime | NO |
| 21 | `opd_mod_times` | int(10,0) | NO |
| 22 | `opd_mod_by` | varchar(12) | NO |
| 23 | `opd_mod_date` | datetime | NO |
| 24 | `opd_char1` | varchar(255) | NO |
| 25 | `opd_char2` | varchar(255) | NO |
| 26 | `opd_char3` | varchar(255) | NO |
| 27 | `opd_char4` | varchar(255) | NO |
| 28 | `opd_char5` | varchar(255) | NO |
| 29 | `opd_char6` | varchar(255) | NO |
| 30 | `opd_qty1` | decimal(19,8) | NO |
| 31 | `opd_qty2` | decimal(19,8) | NO |

### `dbo.pack_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pack_nbr` | varchar(15) | NO |
| 2 | `pack_cinv_nbr` | varchar(15) | NO |
| 3 | `pack_rmks` | varchar(255) | NO |
| 4 | `pack_site` | varchar(8) | NO |
| 5 | `pack_prog_code` | varchar(12) | NO |
| 6 | `pack_crt_by` | varchar(12) | NO |
| 7 | `pack_crt_date` | datetime | NO |
| 8 | `pack_mod_times` | int(10,0) | NO |
| 9 | `pack_mod_by` | varchar(12) | NO |
| 10 | `pack_mod_date` | datetime | NO |
| 11 | `pack_pst` | bit | NO |
| 12 | `pack_pst_by` | varchar(12) | NO |
| 13 | `pack_pst_date` | datetime | YES |
| 14 | `pack_char1` | varchar(255) | NO |
| 15 | `pack_char2` | varchar(255) | NO |
| 16 | `pack_char3` | varchar(255) | NO |
| 17 | `pack_char4` | varchar(255) | NO |
| 18 | `pack_char5` | varchar(255) | NO |
| 19 | `pack_char6` | varchar(255) | NO |
| 20 | `pack_qty1` | decimal(19,8) | NO |
| 21 | `pack_qty2` | decimal(19,8) | NO |

### `dbo.pc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pc_nbr` | varchar(15) | NO |
| 2 | `pc_vend` | varchar(8) | NO |
| 3 | `pc_curr` | varchar(4) | NO |
| 4 | `pc_part` | varchar(30) | NO |
| 5 | `pc_um` | varchar(4) | NO |
| 6 | `pc_um_rate_m` | decimal(19,8) | NO |
| 7 | `pc_um_rate_d` | decimal(19,8) | NO |
| 8 | `pc_start` | datetime | NO |
| 9 | `pc_expire` | datetime | NO |
| 10 | `pc_vat_incl` | bit | NO |
| 11 | `pc_vat` | decimal(19,8) | NO |
| 12 | `pc_type` | varchar(1) | NO |
| 13 | `pc_price_mtl` | decimal(19,8) | NO |
| 14 | `pc_price_sub` | decimal(19,8) | NO |
| 15 | `pc_price` | decimal(19,8) | NO |
| 16 | `pc_rmks` | varchar(255) | NO |
| 17 | `pc_wf_status` | varchar(1) | NO |
| 18 | `pc_crt_by` | varchar(12) | NO |
| 19 | `pc_crt_date` | datetime | NO |
| 20 | `pc_mod_times` | int(10,0) | NO |
| 21 | `pc_mod_by` | varchar(12) | NO |
| 22 | `pc_mod_date` | datetime | NO |
| 23 | `pc_pst` | bit | NO |
| 24 | `pc_pst_by` | varchar(12) | NO |
| 25 | `pc_pst_date` | datetime | YES |
| 26 | `pc_char1` | varchar(255) | NO |
| 27 | `pc_char2` | varchar(255) | NO |
| 28 | `pc_char3` | varchar(255) | NO |
| 29 | `pc_char4` | varchar(255) | NO |
| 30 | `pc_char5` | varchar(255) | NO |
| 31 | `pc_char6` | varchar(255) | NO |
| 32 | `pc_qty1` | decimal(19,8) | NO |
| 33 | `pc_qty2` | decimal(19,8) | NO |
| 34 | `pc_ord_min` | numeric(19,8) | NO |
| 35 | `pc_ord_mult` | numeric(19,8) | NO |
| 36 | `pc_prog_code` | varchar(12) | NO |
| 37 | `pc_qtype` | varchar(2) | NO |
| 38 | `pc_pur_lt` | int(10,0) | NO |
| 39 | `pc_cu_curr` | varchar(4) | NO |
| 40 | `pc_data_src` | varchar(1) | NO |
| 41 | `pc_data_id` | varchar(255) | NO |
| 42 | `pc_allow` | bit | NO |
| 43 | `pc_allow_by` | varchar(12) | NO |
| 44 | `pc_allow_date` | datetime | YES |
| 45 | `pc_chk` | bit | NO |
| 46 | `pc_chk_by` | varchar(12) | NO |
| 47 | `pc_chk_date` | datetime | YES |
| 48 | `pc_sale` | bit | NO |
| 49 | `pc_sale_by` | varchar(12) | NO |
| 50 | `pc_sale_date` | datetime | YES |
| 51 | `pc_op` | int(10,0) | NO |
| 52 | `pc_po_part` | varchar(30) | NO |

### `dbo.pcr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pcr_code` | varchar(15) | NO |
| 2 | `pcr_desc` | varchar(50) | NO |
| 3 | `pcr_rmks` | varchar(255) | NO |
| 4 | `pcr_crt_by` | varchar(12) | NO |
| 5 | `pcr_crt_date` | datetime | NO |
| 6 | `pcr_mod_times` | int(10,0) | NO |
| 7 | `pcr_mod_by` | varchar(12) | NO |
| 8 | `pcr_mod_date` | datetime | NO |
| 9 | `pcr_pst` | bit | NO |
| 10 | `pcr_pst_by` | varchar(12) | NO |
| 11 | `pcr_pst_date` | datetime | YES |
| 12 | `pcr_char1` | varchar(255) | NO |
| 13 | `pcr_char2` | varchar(255) | NO |
| 14 | `pcr_char3` | varchar(255) | NO |
| 15 | `pcr_char4` | varchar(255) | NO |
| 16 | `pcr_char5` | varchar(255) | NO |
| 17 | `pcr_char6` | varchar(255) | NO |
| 18 | `pcr_qty1` | decimal(19,8) | NO |
| 19 | `pcr_qty2` | decimal(19,8) | NO |
| 20 | `pcr_prod_line` | varchar(4) | NO |
| 21 | `pcr_um` | varchar(4) | NO |

### `dbo.pcrd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pcrd_code` | varchar(15) | NO |
| 2 | `pcrd_line` | int(10,0) | NO |
| 3 | `pcrd_desc` | varchar(255) | NO |
| 4 | `pcrd_len` | int(10,0) | NO |
| 5 | `pcrd_is_flow` | bit | NO |
| 6 | `pcrd_split` | varchar(50) | NO |
| 7 | `pcrd_rmks` | varchar(255) | NO |
| 8 | `pcrd_crt_by` | varchar(12) | NO |
| 9 | `pcrd_crt_date` | datetime | NO |
| 10 | `pcrd_mod_times` | int(10,0) | NO |
| 11 | `pcrd_mod_by` | varchar(12) | NO |
| 12 | `pcrd_mod_date` | datetime | NO |
| 13 | `pcrd_char1` | varchar(255) | NO |
| 14 | `pcrd_char2` | varchar(255) | NO |
| 15 | `pcrd_char3` | varchar(255) | NO |
| 16 | `pcrd_char4` | varchar(255) | NO |
| 17 | `pcrd_char5` | varchar(255) | NO |
| 18 | `pcrd_char6` | varchar(255) | NO |
| 19 | `pcrd_qty1` | decimal(19,8) | NO |
| 20 | `pcrd_qty2` | decimal(19,8) | NO |
| 21 | `pcrd_desc_seq` | int(10,0) | NO |
| 22 | `pcrd_chr_flow` | varchar(1) | NO |
| 23 | `pcrd_prefix` | varchar(50) | NO |
| 24 | `pcrd_code_seq` | int(10,0) | NO |
| 25 | `pcrd_desc_name` | varchar(255) | NO |

### `dbo.pcrd2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pcrd2_code` | varchar(15) | NO |
| 2 | `pcrd2_line` | int(10,0) | NO |
| 3 | `pcrd2_option` | varchar(30) | NO |
| 4 | `pcrd2_desc` | varchar(255) | NO |
| 5 | `pcrd2_perms` | varchar(80) | NO |
| 6 | `pcrd2_rmks` | varchar(255) | NO |
| 7 | `pcrd2_crt_by` | varchar(12) | NO |
| 8 | `pcrd2_crt_date` | datetime | NO |
| 9 | `pcrd2_mod_times` | int(10,0) | NO |
| 10 | `pcrd2_mod_by` | varchar(12) | NO |
| 11 | `pcrd2_mod_date` | datetime | NO |
| 12 | `pcrd2_char1` | varchar(255) | NO |
| 13 | `pcrd2_char2` | varchar(255) | NO |
| 14 | `pcrd2_char3` | varchar(255) | NO |
| 15 | `pcrd2_char4` | varchar(255) | NO |
| 16 | `pcrd2_char5` | varchar(255) | NO |
| 17 | `pcrd2_char6` | varchar(255) | NO |
| 18 | `pcrd2_qty1` | decimal(19,8) | NO |
| 19 | `pcrd2_qty2` | decimal(19,8) | NO |
| 20 | `pcrd2_default` | bit | NO |

### `dbo.pcrda_auto` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pcrda_user` | varchar(12) | NO |
| 2 | `pcrda_code` | varchar(15) | NO |
| 3 | `pcrda_line` | int(10,0) | NO |
| 4 | `pcrda_desc` | varchar(255) | NO |
| 5 | `pcrda_is_flow` | bit | NO |
| 6 | `pcrda_len` | int(10,0) | NO |
| 7 | `pcrda_pt_code` | varchar(30) | NO |
| 8 | `pcrda_pt_desc1` | varchar(255) | NO |
| 9 | `pcrda_split` | varchar(50) | NO |
| 10 | `pcrda_readonly` | bit | NO |
| 11 | `pcrda_perms` | varchar(80) | NO |
| 12 | `pcrda_rmks` | varchar(255) | NO |
| 13 | `pcrda_char1` | varchar(255) | NO |
| 14 | `pcrda_char2` | varchar(255) | NO |
| 15 | `pcrda_char3` | varchar(255) | NO |
| 16 | `pcrda_char4` | varchar(255) | NO |
| 17 | `pcrda_char5` | varchar(255) | NO |
| 18 | `pcrda_char6` | varchar(255) | NO |
| 19 | `pcrda_qty1` | decimal(19,8) | NO |
| 20 | `pcrda_qty2` | decimal(19,8) | NO |
| 21 | `pcrda_desc_seq` | int(10,0) | NO |
| 22 | `pcrda_chr_flow` | varchar(1) | NO |
| 23 | `pcrda_prefix` | varchar(50) | NO |
| 24 | `pcrda_code_seq` | int(10,0) | NO |
| 25 | `pcrda_desc_name` | varchar(255) | NO |

### `dbo.pfb_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pfb_pfb` | varchar(15) | NO |
| 2 | `pfb_date` | datetime | NO |
| 3 | `pfb_wkctr` | varchar(8) | NO |
| 4 | `pfb_rmks` | varchar(255) | NO |
| 5 | `pfb_crt_by` | varchar(12) | NO |
| 6 | `pfb_crt_date` | datetime | NO |
| 7 | `pfb_mod_times` | int(10,0) | NO |
| 8 | `pfb_mod_by` | varchar(12) | NO |
| 9 | `pfb_mod_date` | datetime | NO |
| 10 | `pfb_pst` | bit | NO |
| 11 | `pfb_pst_by` | varchar(12) | NO |
| 12 | `pfb_pst_date` | datetime | YES |
| 13 | `pfb_site` | varchar(8) | NO |
| 14 | `pfb_wf_status` | varchar(1) | NO |
| 15 | `pfb_prog_code` | varchar(12) | NO |
| 16 | `pfb_doc_code` | varchar(12) | NO |
| 17 | `pfb_char1` | varchar(255) | NO |
| 18 | `pfb_char2` | varchar(255) | NO |
| 19 | `pfb_char3` | varchar(255) | NO |
| 20 | `pfb_char4` | varchar(255) | NO |
| 21 | `pfb_char5` | varchar(255) | NO |
| 22 | `pfb_char6` | varchar(255) | NO |
| 23 | `pfb_qty1` | decimal(19,8) | NO |
| 24 | `pfb_qty2` | decimal(19,8) | NO |
| 25 | `pfb_sub_line` | varchar(30) | NO |
| 26 | `pfb_data_src` | varchar(1) | NO |
| 27 | `pfb_data_id` | varchar(255) | NO |

### `dbo.pfbd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pfbd_pfb` | varchar(15) | NO |
| 2 | `pfbd_line` | int(10,0) | NO |
| 3 | `pfbd_dpm_nbr` | varchar(15) | NO |
| 4 | `pfbd_dpm_line` | int(10,0) | NO |
| 5 | `pfbd_wkctr` | varchar(8) | NO |
| 6 | `pfbd_emp` | varchar(12) | NO |
| 7 | `pfbd_wr_nbr` | varchar(15) | NO |
| 8 | `pfbd_wr_lot` | varchar(18) | NO |
| 9 | `pfbd_wr_op` | int(10,0) | NO |
| 10 | `pfbd_wr_op2` | int(10,0) | NO |
| 11 | `pfbd_part` | varchar(30) | NO |
| 12 | `pfbd_wr_desc` | varchar(100) | NO |
| 13 | `pfbd_qty_ord` | numeric(19,8) | NO |
| 14 | `pfbd_qty_comp` | numeric(19,8) | NO |
| 15 | `pfbd_qty_rjct` | numeric(19,8) | NO |
| 16 | `pfbd_type` | varchar(1) | NO |
| 17 | `pfbd_start_date` | datetime | NO |
| 18 | `pfbd_start_time` | varchar(10) | NO |
| 19 | `pfbd_stop_date` | datetime | NO |
| 20 | `pfbd_stop_time` | varchar(10) | NO |
| 21 | `pfbd_used_time` | numeric(19,8) | NO |
| 22 | `pfbd_rmks` | varchar(255) | NO |
| 23 | `pfbd_crt_by` | varchar(12) | NO |
| 24 | `pfbd_crt_date` | datetime | NO |
| 25 | `pfbd_mod_times` | int(10,0) | NO |
| 26 | `pfbd_mod_by` | varchar(12) | NO |
| 27 | `pfbd_mod_date` | datetime | NO |
| 28 | `pfbd_char1` | varchar(255) | NO |
| 29 | `pfbd_char2` | varchar(255) | NO |
| 30 | `pfbd_char3` | varchar(255) | NO |
| 31 | `pfbd_char4` | varchar(255) | NO |
| 32 | `pfbd_char5` | varchar(255) | NO |
| 33 | `pfbd_char6` | varchar(255) | NO |
| 34 | `pfbd_qty1` | decimal(19,8) | NO |
| 35 | `pfbd_qty2` | decimal(19,8) | NO |
| 36 | `pfbd_sch_nbr` | varchar(15) | NO |
| 37 | `pfbd_sch_line` | int(10,0) | NO |
| 38 | `pfbd_item_no` | varchar(255) | NO |
| 39 | `pfbd_data_src` | varchar(1) | NO |
| 40 | `pfbd_data_id` | varchar(255) | NO |
| 41 | `pfbd_sub_line` | varchar(30) | NO |

### `dbo.pg_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pg_site` | varchar(8) | NO |
| 2 | `pg_nbr` | varchar(15) | NO |
| 3 | `pg_date` | datetime | NO |
| 4 | `pg_type` | varchar(8) | NO |
| 5 | `pg_part` | varchar(30) | NO |
| 6 | `pg_desc1` | varchar(255) | NO |
| 7 | `pg_t_date` | datetime | YES |
| 8 | `pg_l_date` | datetime | YES |
| 9 | `pg_ele_by` | varchar(12) | NO |
| 10 | `pg_str_by` | varchar(12) | NO |
| 11 | `pg_app_by` | varchar(12) | NO |
| 12 | `pg_emp_gra` | varchar(8) | NO |
| 13 | `pg_sta_date` | datetime | YES |
| 14 | `pg_end_date` | datetime | YES |
| 15 | `pg_status` | varchar(1) | NO |
| 16 | `pg_rmks` | varchar(255) | NO |
| 17 | `pg_wf_status` | varchar(1) | NO |
| 18 | `pg_prog_code` | varchar(12) | NO |
| 19 | `pg_doc_code` | varchar(12) | NO |
| 20 | `pg_crt_by` | varchar(12) | NO |
| 21 | `pg_crt_date` | datetime | NO |
| 22 | `pg_mod_times` | int(10,0) | NO |
| 23 | `pg_mod_by` | varchar(12) | NO |
| 24 | `pg_mod_date` | datetime | NO |
| 25 | `pg_pst` | bit | NO |
| 26 | `pg_pst_by` | varchar(12) | NO |
| 27 | `pg_pst_date` | datetime | YES |
| 28 | `pg_char1` | varchar(255) | NO |
| 29 | `pg_char2` | varchar(255) | NO |
| 30 | `pg_char3` | varchar(255) | NO |
| 31 | `pg_char4` | varchar(255) | NO |
| 32 | `pg_char5` | varchar(255) | NO |
| 33 | `pg_char6` | varchar(255) | NO |
| 34 | `pg_qty1` | decimal(19,8) | NO |
| 35 | `pg_qty2` | decimal(19,8) | NO |

### `dbo.pk_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pk_pk` | varchar(15) | NO |
| 2 | `pk_date` | datetime | NO |
| 3 | `pk_type` | varchar(1) | NO |
| 4 | `pk_wonbr` | varchar(15) | NO |
| 5 | `pk_wolot` | varchar(18) | NO |
| 6 | `pk_rmks` | varchar(255) | NO |
| 7 | `pk_wf_status` | varchar(1) | NO |
| 8 | `pk_site` | varchar(8) | NO |
| 9 | `pk_prog_code` | varchar(12) | NO |
| 10 | `pk_doc_code` | varchar(12) | NO |
| 11 | `pk_crt_by` | varchar(12) | NO |
| 12 | `pk_crt_date` | datetime | NO |
| 13 | `pk_mod_times` | int(10,0) | NO |
| 14 | `pk_mod_by` | varchar(12) | NO |
| 15 | `pk_mod_date` | datetime | NO |
| 16 | `pk_pst` | bit | NO |
| 17 | `pk_pst_by` | varchar(12) | NO |
| 18 | `pk_pst_date` | datetime | YES |
| 19 | `pk_char1` | varchar(255) | NO |
| 20 | `pk_char2` | varchar(255) | NO |
| 21 | `pk_char3` | varchar(255) | NO |
| 22 | `pk_char4` | varchar(255) | NO |
| 23 | `pk_char5` | varchar(255) | NO |
| 24 | `pk_char6` | varchar(255) | NO |
| 25 | `pk_qty1` | decimal(19,8) | NO |
| 26 | `pk_qty2` | decimal(19,8) | NO |
| 27 | `pk_src` | varchar(2) | NO |
| 28 | `pk_src_nbr` | varchar(15) | NO |
| 29 | `pk_chk` | bit | NO |
| 30 | `pk_chk_by` | varchar(12) | NO |
| 31 | `pk_chk_date` | datetime | YES |
| 32 | `pk_data_src` | varchar(1) | NO |
| 33 | `pk_data_id` | varchar(255) | NO |

### `dbo.pkd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pkd_pk` | varchar(15) | NO |
| 2 | `pkd_line` | int(10,0) | NO |
| 3 | `pkd_wo_nbr` | varchar(15) | NO |
| 4 | `pkd_wo_lot` | varchar(18) | NO |
| 5 | `pkd_seq` | int(10,0) | NO |
| 6 | `pkd_type` | varchar(8) | NO |
| 7 | `pkd_part` | varchar(30) | NO |
| 8 | `pkd_qty_req` | numeric(19,8) | NO |
| 9 | `pkd_qty_iss` | numeric(19,8) | NO |
| 10 | `pkd_site` | varchar(8) | NO |
| 11 | `pkd_loc` | varchar(8) | NO |
| 12 | `pkd_lot` | varchar(18) | NO |
| 13 | `pkd_alt` | bit | NO |
| 14 | `pkd_qty_pts_m` | numeric(19,8) | NO |
| 15 | `pkd_qty_pts_d` | numeric(19,8) | NO |
| 16 | `pkd_op` | int(10,0) | NO |
| 17 | `pkd_seq2` | int(10,0) | NO |
| 18 | `pkd_rmks` | varchar(255) | NO |
| 19 | `pkd_crt_by` | varchar(12) | NO |
| 20 | `pkd_crt_date` | datetime | NO |
| 21 | `pkd_mod_times` | int(10,0) | NO |
| 22 | `pkd_mod_by` | varchar(12) | NO |
| 23 | `pkd_mod_date` | datetime | NO |
| 24 | `pkd_char1` | varchar(255) | NO |
| 25 | `pkd_char2` | varchar(255) | NO |
| 26 | `pkd_char3` | varchar(255) | NO |
| 27 | `pkd_char4` | varchar(255) | NO |
| 28 | `pkd_char5` | varchar(255) | NO |
| 29 | `pkd_char6` | varchar(255) | NO |
| 30 | `pkd_qty1` | decimal(19,8) | NO |
| 31 | `pkd_qty2` | decimal(19,8) | NO |
| 32 | `pkd_qty_off` | numeric(19,8) | NO |
| 33 | `pkd_qty_plan` | numeric(19,8) | NO |
| 34 | `pkd_src_nbr` | varchar(15) | NO |
| 35 | `pkd_src_line` | int(10,0) | NO |
| 36 | `pkd_data_src` | varchar(1) | NO |
| 37 | `pkd_data_id` | varchar(255) | NO |

### `dbo.pl_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pl_prod_line` | varchar(4) | NO |
| 2 | `pl_desc` | varchar(30) | NO |
| 3 | `pl_part_type` | varchar(8) | NO |
| 4 | `pl_group` | varchar(8) | NO |
| 5 | `pl_loc` | varchar(8) | NO |
| 6 | `pl_buyer` | varchar(12) | NO |
| 7 | `pl_pm_code` | varchar(1) | NO |
| 8 | `pl_phantom` | bit | NO |
| 9 | `pl_iss_policy` | bit | NO |
| 10 | `pl_memo_item` | bit | NO |
| 11 | `pl_ms` | bit | NO |
| 12 | `pl_keymtl` | bit | NO |
| 13 | `pl_roll_iss` | bit | NO |
| 14 | `pl_ac_code_inv` | varchar(15) | NO |
| 15 | `pl_ac_code_sls` | varchar(15) | NO |
| 16 | `pl_ac_code_comm` | varchar(15) | NO |
| 17 | `pl_ac_code_wcost` | varchar(15) | NO |
| 18 | `pl_ac_code_scost` | varchar(15) | NO |
| 19 | `pl_crt_by` | varchar(12) | NO |
| 20 | `pl_crt_date` | datetime | NO |
| 21 | `pl_char1` | varchar(255) | NO |
| 22 | `pl_char2` | varchar(255) | NO |
| 23 | `pl_char3` | varchar(255) | NO |
| 24 | `pl_char4` | varchar(255) | NO |
| 25 | `pl_char5` | varchar(255) | NO |
| 26 | `pl_char6` | varchar(255) | NO |
| 27 | `pl_qty1` | decimal(19,8) | NO |
| 28 | `pl_qty2` | decimal(19,8) | NO |
| 29 | `pl_insp_req` | bit | NO |
| 30 | `pl_lot_serial` | bit | NO |
| 31 | `pl_lot_grp` | varchar(15) | NO |
| 32 | `pl_view_perms` | varchar(80) | NO |
| 33 | `pl_edit_perms` | varchar(80) | NO |
| 34 | `pl_del_perms` | varchar(80) | NO |
| 35 | `pl_pst_perms` | varchar(80) | NO |
| 36 | `pl_um` | varchar(4) | NO |
| 37 | `pl_backflush` | varchar(1) | NO |
| 38 | `pl_backflush_s` | varchar(1) | NO |
| 39 | `pl_ac_code_shipped` | varchar(15) | NO |
| 40 | `pl_upper` | varchar(15) | NO |
| 41 | `pl_src_prod` | varchar(255) | NO |

### `dbo.pla_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pla_site` | varchar(8) | NO |
| 2 | `pla_nbr` | varchar(15) | NO |
| 3 | `pla_pg_nbr` | varchar(15) | NO |
| 4 | `pla_date` | datetime | NO |
| 5 | `pla_rmks` | varchar(255) | NO |
| 6 | `pla_wf_status` | varchar(1) | NO |
| 7 | `pla_prog_code` | varchar(12) | NO |
| 8 | `pla_doc_code` | varchar(12) | NO |
| 9 | `pla_crt_by` | varchar(12) | NO |
| 10 | `pla_crt_date` | datetime | NO |
| 11 | `pla_mod_times` | int(10,0) | NO |
| 12 | `pla_mod_by` | varchar(12) | NO |
| 13 | `pla_mod_date` | datetime | NO |
| 14 | `pla_pst` | bit | NO |
| 15 | `pla_pst_by` | varchar(12) | NO |
| 16 | `pla_pst_date` | datetime | YES |
| 17 | `pla_char1` | varchar(255) | NO |
| 18 | `pla_char2` | varchar(255) | NO |
| 19 | `pla_char3` | varchar(255) | NO |
| 20 | `pla_char4` | varchar(255) | NO |
| 21 | `pla_char5` | varchar(255) | NO |
| 22 | `pla_char6` | varchar(255) | NO |
| 23 | `pla_qty1` | decimal(19,8) | NO |
| 24 | `pla_qty2` | decimal(19,8) | NO |

### `dbo.plad_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `plad_nbr` | varchar(15) | NO |
| 2 | `plad_line` | int(10,0) | NO |
| 3 | `plad_code` | varchar(8) | NO |
| 4 | `plad_sta_date` | datetime | YES |
| 5 | `plad_pove_date` | datetime | YES |
| 6 | `plad_fove_date` | datetime | YES |
| 7 | `plad_days` | int(10,0) | NO |
| 8 | `plad_manager` | varchar(12) | NO |
| 9 | `plad_cmmt` | varchar(255) | NO |
| 10 | `plad_crt_by` | varchar(12) | NO |
| 11 | `plad_crt_date` | datetime | NO |
| 12 | `plad_mod_times` | int(10,0) | NO |
| 13 | `plad_mod_by` | varchar(12) | NO |
| 14 | `plad_mod_date` | datetime | NO |
| 15 | `plad_char1` | varchar(255) | NO |
| 16 | `plad_char2` | varchar(255) | NO |
| 17 | `plad_char3` | varchar(255) | NO |
| 18 | `plad_char4` | varchar(255) | NO |
| 19 | `plad_char5` | varchar(255) | NO |
| 20 | `plad_char6` | varchar(255) | NO |
| 21 | `plad_qty1` | decimal(19,8) | NO |
| 22 | `plad_qty2` | decimal(19,8) | NO |

### `dbo.pm_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pm_company` | varchar(8) | NO |
| 2 | `pm_nbr` | varchar(15) | NO |
| 3 | `pm_doc_code` | varchar(15) | NO |
| 4 | `pm_date` | datetime | NO |
| 5 | `pm_vendor` | varchar(8) | NO |
| 6 | `pm_curr` | varchar(4) | NO |
| 7 | `pm_rmks` | varchar(255) | NO |
| 8 | `pm_vo_nbr` | varchar(15) | NO |
| 9 | `pm_prn_cnt` | int(10,0) | NO |
| 10 | `pm_base_debit_tot` | numeric(19,8) | NO |
| 11 | `pm_base_credit_tot` | numeric(19,8) | NO |
| 12 | `pm_prog_code` | varchar(12) | NO |
| 13 | `pm_crt_by` | varchar(12) | NO |
| 14 | `pm_crt_date` | datetime | NO |
| 15 | `pm_mod_times` | int(10,0) | NO |
| 16 | `pm_mod_by` | varchar(12) | NO |
| 17 | `pm_mod_date` | datetime | NO |
| 18 | `pm_pst` | bit | NO |
| 19 | `pm_pst_by` | varchar(12) | NO |
| 20 | `pm_pst_date` | datetime | YES |
| 21 | `pm_char1` | varchar(255) | NO |
| 22 | `pm_char2` | varchar(255) | NO |
| 23 | `pm_char3` | varchar(255) | NO |
| 24 | `pm_char4` | varchar(255) | NO |
| 25 | `pm_char5` | varchar(255) | NO |
| 26 | `pm_char6` | varchar(255) | NO |
| 27 | `pm_qty1` | decimal(19,8) | NO |
| 28 | `pm_qty2` | decimal(19,8) | NO |

### `dbo.pma_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pma_nbr` | varchar(15) | NO |
| 2 | `pma_date` | datetime | NO |
| 3 | `pma_vend` | varchar(30) | NO |
| 4 | `pma_bank` | varchar(255) | NO |
| 5 | `pma_account` | varchar(255) | NO |
| 6 | `pma_curr` | varchar(4) | NO |
| 7 | `pma_cr_terms` | varchar(10) | NO |
| 8 | `pma_usage` | varchar(30) | NO |
| 9 | `pma_bill_info` | varchar(30) | NO |
| 10 | `pma_bill_date` | datetime | YES |
| 11 | `pma_attach_cnt` | int(10,0) | NO |
| 12 | `pma_rmks` | varchar(255) | NO |
| 13 | `pma_pay_date` | datetime | YES |
| 14 | `pma_pm_nbr` | varchar(15) | NO |
| 15 | `pma_crt_by` | varchar(12) | NO |
| 16 | `pma_crt_date` | datetime | NO |
| 17 | `pma_mod_times` | int(10,0) | NO |
| 18 | `pma_mod_by` | varchar(12) | NO |
| 19 | `pma_mod_date` | datetime | NO |
| 20 | `pma_pst` | bit | NO |
| 21 | `pma_pst_by` | varchar(12) | NO |
| 22 | `pma_pst_date` | datetime | YES |
| 23 | `pma_chk` | bit | NO |
| 24 | `pma_chk_by` | varchar(12) | NO |
| 25 | `pma_chk_date` | datetime | YES |
| 26 | `pma_char1` | varchar(255) | NO |
| 27 | `pma_char2` | varchar(255) | NO |
| 28 | `pma_char3` | varchar(255) | NO |
| 29 | `pma_char4` | varchar(255) | NO |
| 30 | `pma_char5` | varchar(255) | NO |
| 31 | `pma_char6` | varchar(255) | NO |
| 32 | `pma_qty1` | decimal(19,8) | NO |
| 33 | `pma_qty2` | decimal(19,8) | NO |

### `dbo.pmad_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pmad_nbr` | varchar(15) | NO |
| 2 | `pmad_line` | int(10,0) | NO |
| 3 | `pmad_type` | varchar(1) | NO |
| 4 | `pmad_ap_nbr` | varchar(15) | NO |
| 5 | `pmad_po_nbr` | varchar(15) | NO |
| 6 | `pmad_content` | varchar(255) | NO |
| 7 | `pmad_curr` | varchar(4) | NO |
| 8 | `pmad_tot_amt` | numeric(19,8) | NO |
| 9 | `pmad_paid_amt` | numeric(19,8) | NO |
| 10 | `pmad_pay_amt` | numeric(19,8) | NO |
| 11 | `pmad_pay_rate` | numeric(19,8) | NO |
| 12 | `pmad_status` | varchar(1) | NO |
| 13 | `pmad_ac_code` | varchar(15) | NO |
| 14 | `pmad_rmks` | varchar(255) | NO |
| 15 | `pmad_crt_by` | varchar(12) | NO |
| 16 | `pmad_crt_date` | datetime | NO |
| 17 | `pmad_mod_times` | int(10,0) | NO |
| 18 | `pmad_mod_by` | varchar(12) | NO |
| 19 | `pmad_mod_date` | datetime | NO |
| 20 | `pmad_char1` | varchar(255) | NO |
| 21 | `pmad_char2` | varchar(255) | NO |
| 22 | `pmad_char3` | varchar(255) | NO |
| 23 | `pmad_char4` | varchar(255) | NO |
| 24 | `pmad_char5` | varchar(255) | NO |
| 25 | `pmad_char6` | varchar(255) | NO |
| 26 | `pmad_qty1` | decimal(19,8) | NO |
| 27 | `pmad_qty2` | decimal(19,8) | NO |

### `dbo.pmd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pmd_nbr` | varchar(15) | NO |
| 2 | `pmd_line` | int(10,0) | NO |
| 3 | `pmd_d_c` | varchar(1) | NO |
| 4 | `pmd_type` | varchar(1) | NO |
| 5 | `pmd_src_doc` | varchar(15) | NO |
| 6 | `pmd_src_nbr` | varchar(15) | NO |
| 7 | `pmd_ac_code` | varchar(15) | NO |
| 8 | `pmd_due_date` | datetime | YES |
| 9 | `pmd_curr` | varchar(4) | NO |
| 10 | `pmd_exch_rate` | decimal(19,8) | NO |
| 11 | `pmd_last_exch_rate` | decimal(19,8) | NO |
| 12 | `pmd_ap_amt` | numeric(19,8) | NO |
| 13 | `pmd_open_amt` | numeric(19,8) | NO |
| 14 | `pmd_pay_amt` | numeric(19,8) | NO |
| 15 | `pmd_pay_base` | numeric(19,8) | NO |
| 16 | `pmd_rmks` | varchar(255) | NO |
| 17 | `pmd_dept` | varchar(10) | NO |
| 18 | `pmd_analy1_code` | varchar(30) | NO |
| 19 | `pmd_analy1_name` | varchar(255) | NO |
| 20 | `pmd_analy2_code` | varchar(30) | NO |
| 21 | `pmd_analy2_name` | varchar(255) | NO |
| 22 | `pmd_analy3_code` | varchar(30) | NO |
| 23 | `pmd_analy3_name` | varchar(255) | NO |
| 24 | `pmd_analy4_code` | varchar(30) | NO |
| 25 | `pmd_analy4_name` | varchar(255) | NO |
| 26 | `pmd_crt_by` | varchar(12) | NO |
| 27 | `pmd_crt_date` | datetime | NO |
| 28 | `pmd_mod_times` | int(10,0) | NO |
| 29 | `pmd_mod_by` | varchar(12) | NO |
| 30 | `pmd_mod_date` | datetime | NO |
| 31 | `pmd_char1` | varchar(255) | NO |
| 32 | `pmd_char2` | varchar(255) | NO |
| 33 | `pmd_char3` | varchar(255) | NO |
| 34 | `pmd_char4` | varchar(255) | NO |
| 35 | `pmd_char5` | varchar(255) | NO |
| 36 | `pmd_char6` | varchar(255) | NO |
| 37 | `pmd_qty1` | decimal(19,8) | NO |
| 38 | `pmd_qty2` | decimal(19,8) | NO |
| 39 | `pmd_capf_flow` | int(10,0) | NO |

### `dbo.po_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `po_nbr` | varchar(15) | NO |
| 2 | `po_vend` | varchar(8) | NO |
| 3 | `po_ship` | varchar(8) | NO |
| 4 | `po_bill` | varchar(8) | NO |
| 5 | `po_ord_date` | datetime | NO |
| 6 | `po_buyer` | varchar(12) | NO |
| 7 | `po_curr` | varchar(4) | NO |
| 8 | `po_ex_rate` | decimal(19,8) | NO |
| 9 | `po_vat` | decimal(19,8) | NO |
| 10 | `po_cr_terms` | varchar(10) | NO |
| 11 | `po_rmks` | varchar(255) | NO |
| 12 | `po_type` | varchar(1) | NO |
| 13 | `po_type2` | varchar(10) | NO |
| 14 | `po_rev` | varchar(4) | NO |
| 15 | `po_terms` | text(2147483647) | YES |
| 16 | `po_wf_status` | varchar(1) | NO |
| 17 | `po_site` | varchar(8) | NO |
| 18 | `po_prog_code` | varchar(12) | NO |
| 19 | `po_doc_code` | varchar(12) | NO |
| 20 | `po_crt_by` | varchar(12) | NO |
| 21 | `po_crt_date` | datetime | NO |
| 22 | `po_mod_times` | int(10,0) | NO |
| 23 | `po_mod_by` | varchar(12) | NO |
| 24 | `po_mod_date` | datetime | NO |
| 25 | `po_pst` | bit | NO |
| 26 | `po_pst_by` | varchar(12) | NO |
| 27 | `po_pst_date` | datetime | YES |
| 28 | `po_chk` | bit | NO |
| 29 | `po_chk_by` | varchar(12) | NO |
| 30 | `po_chk_date` | datetime | YES |
| 31 | `po_char1` | varchar(255) | NO |
| 32 | `po_char2` | varchar(255) | NO |
| 33 | `po_char3` | varchar(255) | NO |
| 34 | `po_char4` | varchar(255) | NO |
| 35 | `po_char5` | varchar(255) | NO |
| 36 | `po_char6` | varchar(255) | NO |
| 37 | `po_qty1` | decimal(19,8) | NO |
| 38 | `po_qty2` | decimal(19,8) | NO |
| 39 | `po_data_src` | varchar(1) | NO |
| 40 | `po_data_id` | varchar(255) | NO |
| 41 | `po_src` | varchar(2) | NO |
| 42 | `po_src_nbr` | varchar(15) | NO |
| 43 | `po_src_lot` | varchar(18) | NO |
| 44 | `po_cfm` | bit | NO |
| 45 | `po_cfm_by` | varchar(12) | NO |
| 46 | `po_cfm_date` | datetime | YES |

### `dbo.poc_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `poc_poc` | int(10,0) | NO |
| 2 | `poc_ship` | varchar(8) | NO |
| 3 | `poc_bill` | varchar(8) | NO |
| 4 | `poc_naprv_vendor` | varchar(255) | NO |
| 5 | `poc_naprv_part` | varchar(255) | NO |
| 6 | `poc_mod_price` | varchar(255) | NO |
| 7 | `poc_all_vend` | varchar(255) | NO |
| 8 | `poc_price_clue` | varchar(1) | NO |
| 9 | `poc_zero_price_pur` | varchar(255) | NO |
| 10 | `poc_pr_needed` | bit | NO |
| 11 | `poc_outpr_needed` | bit | NO |
| 12 | `poc_pr_m_needed` | bit | NO |
| 13 | `poc_replace` | bit | NO |
| 14 | `poc_terms` | text(2147483647) | YES |
| 15 | `poc_char1` | varchar(255) | NO |
| 16 | `poc_char2` | varchar(255) | NO |
| 17 | `poc_char3` | varchar(255) | NO |
| 18 | `poc_char4` | varchar(255) | NO |
| 19 | `poc_char5` | varchar(255) | NO |
| 20 | `poc_char6` | varchar(255) | NO |
| 21 | `poc_qty1` | decimal(19,8) | NO |
| 22 | `poc_qty2` | decimal(19,8) | NO |
| 23 | `poc_mod_price2` | varchar(255) | NO |
| 24 | `poc_zero_price_pur2` | varchar(255) | NO |
| 25 | `poc_adv_rcv_days` | int(10,0) | NO |
| 26 | `poc_adv_rcv_ctrl` | varchar(1) | NO |
| 27 | `poc_iqc_qc` | bit | NO |
| 28 | `poc_select_vend` | varchar(255) | NO |
| 29 | `poc_select_vend2` | varchar(255) | NO |
| 30 | `poc_max_price_perm` | varchar(255) | NO |
| 31 | `poc_adv_rcv_date` | varchar(1) | NO |
| 32 | `poc_adv_rcv_type` | varchar(1) | NO |
| 33 | `poc_samp_vend` | varchar(255) | NO |
| 34 | `poc_samp_mod_price` | varchar(255) | NO |
| 35 | `poc_samp_zero_price` | varchar(255) | NO |
| 36 | `poc_samp_gen_po` | varchar(255) | NO |
| 37 | `poc_strategic_vend` | varchar(255) | NO |
| 38 | `poc_ordinary_vend` | varchar(255) | NO |
| 39 | `poc_strategic_vend_price` | varchar(255) | NO |

### `dbo.pod_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pod_nbr` | varchar(15) | NO |
| 2 | `pod_line` | int(10,0) | NO |
| 3 | `pod_req` | varchar(15) | NO |
| 4 | `pod_req_line` | int(10,0) | NO |
| 5 | `pod_part` | varchar(30) | NO |
| 6 | `pod_vpart` | varchar(30) | NO |
| 7 | `pod_um` | varchar(4) | NO |
| 8 | `pod_um_rate_m` | decimal(19,8) | NO |
| 9 | `pod_um_rate_d` | decimal(19,8) | NO |
| 10 | `pod_qty_ord` | numeric(19,8) | NO |
| 11 | `pod_qty_spare` | numeric(19,8) | NO |
| 12 | `pod_qty_rcvd` | numeric(19,8) | NO |
| 13 | `pod_qty_spare_rcvd` | numeric(19,8) | NO |
| 14 | `pod_qty_rtnd` | numeric(19,8) | NO |
| 15 | `pod_qty_spare_rtn` | numeric(19,8) | NO |
| 16 | `pod_qty_ex` | numeric(19,8) | NO |
| 17 | `pod_pur_cost` | decimal(19,8) | NO |
| 18 | `pod_need` | datetime | NO |
| 19 | `pod_due_date` | datetime | NO |
| 20 | `pod_promise_date` | datetime | YES |
| 21 | `pod_so_nbr` | varchar(15) | NO |
| 22 | `pod_wo_nbr` | varchar(15) | NO |
| 23 | `pod_wo_lot` | varchar(18) | NO |
| 24 | `pod_rtn_flag` | bit | NO |
| 25 | `pod_rmks` | varchar(255) | NO |
| 26 | `pod_status` | varchar(1) | NO |
| 27 | `pod_crt_by` | varchar(12) | NO |
| 28 | `pod_crt_date` | datetime | NO |
| 29 | `pod_mod_times` | int(10,0) | NO |
| 30 | `pod_mod_by` | varchar(12) | NO |
| 31 | `pod_mod_date` | datetime | NO |
| 32 | `pod_close_by` | varchar(12) | NO |
| 33 | `pod_close_date` | datetime | YES |
| 34 | `pod_pt_desc` | varchar(255) | NO |
| 35 | `pod_ac_mtl` | varchar(15) | NO |
| 36 | `pod_char1` | varchar(255) | NO |
| 37 | `pod_char2` | varchar(255) | NO |
| 38 | `pod_char3` | varchar(255) | NO |
| 39 | `pod_char4` | varchar(255) | NO |
| 40 | `pod_char5` | varchar(255) | NO |
| 41 | `pod_char6` | varchar(255) | NO |
| 42 | `pod_qty1` | decimal(19,8) | NO |
| 43 | `pod_qty2` | decimal(19,8) | NO |
| 44 | `pod_dept` | varchar(10) | NO |
| 45 | `pod_qty_rcvd_inv` | numeric(19,8) | NO |
| 46 | `pod_qty_rtnd_inv` | numeric(19,8) | NO |
| 47 | `pod_qty_spare_rcvd_inv` | numeric(19,8) | NO |
| 48 | `pod_qty_spare_rtn_inv` | numeric(19,8) | NO |
| 49 | `pod_qty_addi` | numeric(19,8) | NO |
| 50 | `pod_cu_price` | decimal(19,8) | NO |
| 51 | `pod_so_line` | int(10,0) | NO |
| 52 | `pod_cu_curr` | varchar(4) | NO |
| 53 | `pod_qty_rcvd_acpt` | numeric(19,8) | NO |
| 54 | `pod_qty_rcvd_acpt_inv` | numeric(19,8) | NO |
| 55 | `pod_qty_rcvd_spare_acpt` | numeric(19,8) | NO |
| 56 | `pod_qty_rcvd_spare_acpt_inv` | numeric(19,8) | NO |
| 57 | `pod_data_src` | varchar(1) | NO |
| 58 | `pod_data_id` | varchar(255) | NO |
| 59 | `pod_close_reason` | varchar(255) | NO |

### `dbo.pod_det20260522` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prh_flow_no` | int(10,0) | NO |
| 2 | `prh_site` | varchar(8) | NO |
| 3 | `prh_nbr` | varchar(15) | NO |
| 4 | `prh_line` | int(10,0) | NO |
| 5 | `prh_receiver` | varchar(15) | NO |
| 6 | `prh_grnd_line` | int(10,0) | NO |
| 7 | `prh_rcp_date` | datetime | NO |
| 8 | `prh_ord_date` | datetime | NO |
| 9 | `prh_due_date` | datetime | NO |
| 10 | `prh_vend` | varchar(8) | NO |
| 11 | `prh_part` | varchar(30) | NO |
| 12 | `prh_vpart` | varchar(30) | NO |
| 13 | `prh_ps_nbr` | varchar(30) | NO |
| 14 | `prh_qty_ord` | numeric(19,8) | NO |
| 15 | `prh_qty_spare` | numeric(19,8) | NO |
| 16 | `prh_qty_rcvd` | numeric(19,8) | NO |
| 17 | `prh_qty_spare_rcvd` | numeric(19,8) | NO |
| 18 | `prh_um` | varchar(4) | NO |
| 19 | `prh_um_rate_m` | decimal(19,8) | NO |
| 20 | `prh_um_rate_d` | decimal(19,8) | NO |
| 21 | `prh_pur_cost` | decimal(19,8) | NO |
| 22 | `prh_curr` | varchar(4) | NO |
| 23 | `prh_ex_rate` | decimal(19,8) | NO |
| 24 | `prh_vat` | decimal(19,8) | NO |
| 25 | `prh_rcp_type` | varchar(1) | NO |
| 26 | `prh_buyer` | varchar(12) | NO |
| 27 | `prh_crt_by` | varchar(12) | NO |
| 28 | `prh_crt_date` | datetime | NO |
| 29 | `prh_char1` | varchar(255) | NO |
| 30 | `prh_char2` | varchar(255) | NO |
| 31 | `prh_char3` | varchar(255) | NO |
| 32 | `prh_char4` | varchar(255) | NO |
| 33 | `prh_char5` | varchar(255) | NO |
| 34 | `prh_char6` | varchar(255) | NO |
| 35 | `prh_qty1` | decimal(19,8) | NO |
| 36 | `prh_qty2` | decimal(19,8) | NO |
| 37 | `prh_pt_desc` | varchar(255) | NO |
| 38 | `prh_dept` | varchar(10) | NO |
| 39 | `prh_src_nbr` | varchar(15) | NO |
| 40 | `prh_src_line` | int(10,0) | NO |
| 41 | `pod_nbr` | varchar(15) | NO |
| 42 | `pod_line` | int(10,0) | NO |
| 43 | `pod_req` | varchar(15) | NO |
| 44 | `pod_req_line` | int(10,0) | NO |
| 45 | `pod_part` | varchar(30) | NO |
| 46 | `pod_vpart` | varchar(30) | NO |
| 47 | `pod_um` | varchar(4) | NO |
| 48 | `pod_um_rate_m` | decimal(19,8) | NO |
| 49 | `pod_um_rate_d` | decimal(19,8) | NO |
| 50 | `pod_qty_ord` | numeric(19,8) | NO |
| 51 | `pod_qty_spare` | numeric(19,8) | NO |
| 52 | `pod_qty_rcvd` | numeric(19,8) | NO |
| 53 | `pod_qty_spare_rcvd` | numeric(19,8) | NO |
| 54 | `pod_qty_rtnd` | numeric(19,8) | NO |
| 55 | `pod_qty_spare_rtn` | numeric(19,8) | NO |
| 56 | `pod_qty_ex` | numeric(19,8) | NO |
| 57 | `pod_pur_cost` | decimal(19,8) | NO |
| 58 | `pod_need` | datetime | NO |
| 59 | `pod_due_date` | datetime | NO |
| 60 | `pod_promise_date` | datetime | YES |
| 61 | `pod_so_nbr` | varchar(15) | NO |
| 62 | `pod_wo_nbr` | varchar(15) | NO |
| 63 | `pod_wo_lot` | varchar(18) | NO |
| 64 | `pod_rtn_flag` | bit | NO |
| 65 | `pod_rmks` | varchar(255) | NO |
| 66 | `pod_status` | varchar(1) | NO |
| 67 | `pod_crt_by` | varchar(12) | NO |
| 68 | `pod_crt_date` | datetime | NO |
| 69 | `pod_mod_times` | int(10,0) | NO |
| 70 | `pod_mod_by` | varchar(12) | NO |
| 71 | `pod_mod_date` | datetime | NO |
| 72 | `pod_close_by` | varchar(12) | NO |
| 73 | `pod_close_date` | datetime | YES |
| 74 | `pod_pt_desc` | varchar(255) | NO |
| 75 | `pod_ac_mtl` | varchar(15) | NO |
| 76 | `pod_char1` | varchar(255) | NO |
| 77 | `pod_char2` | varchar(255) | NO |
| 78 | `pod_char3` | varchar(255) | NO |
| 79 | `pod_char4` | varchar(255) | NO |
| 80 | `pod_char5` | varchar(255) | NO |
| 81 | `pod_char6` | varchar(255) | NO |
| 82 | `pod_qty1` | decimal(19,8) | NO |
| 83 | `pod_qty2` | decimal(19,8) | NO |
| 84 | `pod_dept` | varchar(10) | NO |
| 85 | `pod_qty_rcvd_inv` | numeric(19,8) | NO |
| 86 | `pod_qty_rtnd_inv` | numeric(19,8) | NO |
| 87 | `pod_qty_spare_rcvd_inv` | numeric(19,8) | NO |
| 88 | `pod_qty_spare_rtn_inv` | numeric(19,8) | NO |
| 89 | `pod_qty_addi` | numeric(19,8) | NO |
| 90 | `pod_cu_price` | decimal(19,8) | NO |
| 91 | `pod_so_line` | int(10,0) | NO |
| 92 | `pod_cu_curr` | varchar(4) | NO |
| 93 | `pod_qty_rcvd_acpt` | numeric(19,8) | NO |
| 94 | `pod_qty_rcvd_acpt_inv` | numeric(19,8) | NO |
| 95 | `pod_qty_rcvd_spare_acpt` | numeric(19,8) | NO |
| 96 | `pod_qty_rcvd_spare_acpt_inv` | numeric(19,8) | NO |
| 97 | `pod_data_src` | varchar(1) | NO |
| 98 | `pod_data_id` | varchar(255) | NO |
| 99 | `pod_close_reason` | varchar(255) | NO |

### `dbo.pom_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pom_po_nbr` | varchar(15) | NO |
| 2 | `pom_po_rev` | varchar(4) | NO |
| 3 | `pom_bf_po_rev` | varchar(4) | NO |
| 4 | `pom_bf_po_ship` | varchar(8) | NO |
| 5 | `pom_bf_po_bill` | varchar(8) | NO |
| 6 | `pom_bf_po_cr_terms` | varchar(10) | NO |
| 7 | `pom_bf_po_buyer` | varchar(12) | NO |
| 8 | `pom_bf_po_curr` | varchar(4) | NO |
| 9 | `pom_bf_po_ex_rate` | decimal(19,8) | NO |
| 10 | `pom_bf_po_vat` | decimal(19,8) | NO |
| 11 | `pom_bf_po_rmks` | varchar(255) | NO |
| 12 | `pom_bf_po_terms` | text(2147483647) | YES |
| 13 | `pom_bf_po_char1` | varchar(255) | NO |
| 14 | `pom_bf_po_char2` | varchar(255) | NO |
| 15 | `pom_bf_po_char3` | varchar(255) | NO |
| 16 | `pom_bf_po_char4` | varchar(255) | NO |
| 17 | `pom_bf_po_char5` | varchar(255) | NO |
| 18 | `pom_bf_po_char6` | varchar(255) | NO |
| 19 | `pom_bf_po_qty1` | decimal(19,8) | NO |
| 20 | `pom_bf_po_qty2` | decimal(19,8) | NO |
| 21 | `pom_af_po_ship` | varchar(8) | NO |
| 22 | `pom_af_po_bill` | varchar(8) | NO |
| 23 | `pom_af_po_cr_terms` | varchar(10) | NO |
| 24 | `pom_af_po_buyer` | varchar(12) | NO |
| 25 | `pom_af_po_curr` | varchar(4) | NO |
| 26 | `pom_af_po_ex_rate` | decimal(19,8) | NO |
| 27 | `pom_af_po_vat` | decimal(19,8) | NO |
| 28 | `pom_af_po_rmks` | varchar(255) | NO |
| 29 | `pom_af_po_terms` | text(2147483647) | YES |
| 30 | `pom_af_po_char1` | varchar(255) | NO |
| 31 | `pom_af_po_char2` | varchar(255) | NO |
| 32 | `pom_af_po_char3` | varchar(255) | NO |
| 33 | `pom_af_po_char4` | varchar(255) | NO |
| 34 | `pom_af_po_char5` | varchar(255) | NO |
| 35 | `pom_af_po_char6` | varchar(255) | NO |
| 36 | `pom_af_po_qty1` | decimal(19,8) | NO |
| 37 | `pom_af_po_qty2` | decimal(19,8) | NO |
| 38 | `pom_rmks` | varchar(255) | NO |
| 39 | `pom_site` | varchar(8) | NO |
| 40 | `pom_prog_code` | varchar(12) | NO |
| 41 | `pom_doc_code` | varchar(12) | NO |
| 42 | `pom_wf_status` | varchar(1) | NO |
| 43 | `pom_crt_by` | varchar(12) | NO |
| 44 | `pom_crt_date` | datetime | NO |
| 45 | `pom_mod_times` | int(10,0) | NO |
| 46 | `pom_mod_by` | varchar(12) | NO |
| 47 | `pom_mod_date` | datetime | NO |
| 48 | `pom_pst` | bit | NO |
| 49 | `pom_pst_by` | varchar(12) | NO |
| 50 | `pom_pst_date` | datetime | YES |
| 51 | `pom_char1` | varchar(255) | NO |
| 52 | `pom_char2` | varchar(255) | NO |
| 53 | `pom_char3` | varchar(255) | NO |
| 54 | `pom_char4` | varchar(255) | NO |
| 55 | `pom_char5` | varchar(255) | NO |
| 56 | `pom_char6` | varchar(255) | NO |
| 57 | `pom_qty1` | decimal(19,8) | NO |
| 58 | `pom_qty2` | decimal(19,8) | NO |

### `dbo.pomd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pomd_po_nbr` | varchar(15) | NO |
| 2 | `pomd_po_rev` | varchar(4) | NO |
| 3 | `pomd_line` | int(10,0) | NO |
| 4 | `pomd_type` | varchar(1) | NO |
| 5 | `pomd_pod_line` | int(10,0) | NO |
| 6 | `pomd_pod_req` | varchar(15) | NO |
| 7 | `pomd_pod_req_line` | int(10,0) | NO |
| 8 | `pomd_pod_part` | varchar(30) | NO |
| 9 | `pomd_pod_vpart` | varchar(30) | NO |
| 10 | `pomd_pod_um` | varchar(4) | NO |
| 11 | `pomd_bf_pod_qty_ord` | numeric(19,8) | NO |
| 12 | `pomd_bf_pod_qty_spare` | numeric(19,8) | NO |
| 13 | `pomd_bf_pod_qty_ex` | numeric(19,8) | NO |
| 14 | `pomd_bf_pod_pur_cost` | decimal(19,8) | NO |
| 15 | `pomd_bf_pod_need` | datetime | YES |
| 16 | `pomd_bf_pod_due_date` | datetime | YES |
| 17 | `pomd_bf_pod_promise_date` | datetime | YES |
| 18 | `pomd_bf_pod_um_rate_m` | decimal(19,8) | NO |
| 19 | `pomd_bf_pod_um_rate_d` | decimal(19,8) | NO |
| 20 | `pomd_bf_pod_char1` | varchar(255) | NO |
| 21 | `pomd_bf_pod_char2` | varchar(255) | NO |
| 22 | `pomd_bf_pod_char3` | varchar(255) | NO |
| 23 | `pomd_bf_pod_char4` | varchar(255) | NO |
| 24 | `pomd_bf_pod_char5` | varchar(255) | NO |
| 25 | `pomd_bf_pod_char6` | varchar(255) | NO |
| 26 | `pomd_bf_pod_qty1` | decimal(19,8) | NO |
| 27 | `pomd_bf_pod_qty2` | decimal(19,8) | NO |
| 28 | `pomd_af_pod_qty_ord` | numeric(19,8) | NO |
| 29 | `pomd_af_pod_qty_spare` | numeric(19,8) | NO |
| 30 | `pomd_af_pod_qty_ex` | numeric(19,8) | NO |
| 31 | `pomd_af_pod_pur_cost` | decimal(19,8) | NO |
| 32 | `pomd_af_pod_need` | datetime | NO |
| 33 | `pomd_af_pod_due_date` | datetime | NO |
| 34 | `pomd_af_pod_promise_date` | datetime | YES |
| 35 | `pomd_af_pod_um_rate_m` | decimal(19,8) | NO |
| 36 | `pomd_af_pod_um_rate_d` | decimal(19,8) | NO |
| 37 | `pomd_af_pod_char1` | varchar(255) | NO |
| 38 | `pomd_af_pod_char2` | varchar(255) | NO |
| 39 | `pomd_af_pod_char3` | varchar(255) | NO |
| 40 | `pomd_af_pod_char4` | varchar(255) | NO |
| 41 | `pomd_af_pod_char5` | varchar(255) | NO |
| 42 | `pomd_af_pod_char6` | varchar(255) | NO |
| 43 | `pomd_af_pod_qty1` | decimal(19,8) | NO |
| 44 | `pomd_af_pod_qty2` | decimal(19,8) | NO |
| 45 | `pomd_reason` | varchar(255) | NO |
| 46 | `pomd_rmks` | varchar(255) | NO |
| 47 | `pomd_crt_by` | varchar(12) | NO |
| 48 | `pomd_crt_date` | datetime | NO |
| 49 | `pomd_mod_times` | int(10,0) | NO |
| 50 | `pomd_mod_by` | varchar(12) | NO |
| 51 | `pomd_mod_date` | datetime | NO |
| 52 | `pomd_char1` | varchar(255) | NO |
| 53 | `pomd_char2` | varchar(255) | NO |
| 54 | `pomd_char3` | varchar(255) | NO |
| 55 | `pomd_char4` | varchar(255) | NO |
| 56 | `pomd_char5` | varchar(255) | NO |
| 57 | `pomd_char6` | varchar(255) | NO |
| 58 | `pomd_qty1` | decimal(19,8) | NO |
| 59 | `pomd_qty2` | decimal(19,8) | NO |
| 60 | `pomd_bf_pod_cu_price` | decimal(19,8) | NO |
| 61 | `pomd_af_pod_cu_price` | decimal(19,8) | NO |

### `dbo.pr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pr_nbr` | varchar(15) | NO |
| 2 | `pr_rel_date` | datetime | NO |
| 3 | `pr_req_by` | varchar(12) | NO |
| 4 | `pr_type` | varchar(1) | NO |
| 5 | `pr_rmks` | varchar(255) | NO |
| 6 | `pr_wf_status` | varchar(1) | NO |
| 7 | `pr_site` | varchar(8) | NO |
| 8 | `pr_prog_code` | varchar(12) | NO |
| 9 | `pr_doc_code` | varchar(12) | NO |
| 10 | `pr_crt_by` | varchar(12) | NO |
| 11 | `pr_crt_date` | datetime | NO |
| 12 | `pr_mod_times` | int(10,0) | NO |
| 13 | `pr_mod_by` | varchar(12) | NO |
| 14 | `pr_mod_date` | datetime | NO |
| 15 | `pr_pst` | bit | NO |
| 16 | `pr_pst_by` | varchar(12) | NO |
| 17 | `pr_pst_date` | datetime | YES |
| 18 | `pr_char1` | varchar(255) | NO |
| 19 | `pr_char2` | varchar(255) | NO |
| 20 | `pr_char3` | varchar(255) | NO |
| 21 | `pr_char4` | varchar(255) | NO |
| 22 | `pr_char5` | varchar(255) | NO |
| 23 | `pr_char6` | varchar(255) | NO |
| 24 | `pr_qty1` | decimal(19,8) | NO |
| 25 | `pr_qty2` | decimal(19,8) | NO |
| 26 | `pr_dept` | varchar(10) | NO |
| 27 | `pr_src` | varchar(2) | NO |
| 28 | `pr_src_nbr` | varchar(15) | NO |
| 29 | `pr_src_lot` | varchar(18) | NO |

### `dbo.prh_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prh_flow_no` | int(10,0) | NO |
| 2 | `prh_site` | varchar(8) | NO |
| 3 | `prh_nbr` | varchar(15) | NO |
| 4 | `prh_line` | int(10,0) | NO |
| 5 | `prh_receiver` | varchar(15) | NO |
| 6 | `prh_grnd_line` | int(10,0) | NO |
| 7 | `prh_rcp_date` | datetime | NO |
| 8 | `prh_ord_date` | datetime | NO |
| 9 | `prh_due_date` | datetime | NO |
| 10 | `prh_vend` | varchar(8) | NO |
| 11 | `prh_part` | varchar(30) | NO |
| 12 | `prh_vpart` | varchar(30) | NO |
| 13 | `prh_ps_nbr` | varchar(30) | NO |
| 14 | `prh_qty_ord` | numeric(19,8) | NO |
| 15 | `prh_qty_spare` | numeric(19,8) | NO |
| 16 | `prh_qty_rcvd` | numeric(19,8) | NO |
| 17 | `prh_qty_spare_rcvd` | numeric(19,8) | NO |
| 18 | `prh_um` | varchar(4) | NO |
| 19 | `prh_um_rate_m` | decimal(19,8) | NO |
| 20 | `prh_um_rate_d` | decimal(19,8) | NO |
| 21 | `prh_pur_cost` | decimal(19,8) | NO |
| 22 | `prh_curr` | varchar(4) | NO |
| 23 | `prh_ex_rate` | decimal(19,8) | NO |
| 24 | `prh_vat` | decimal(19,8) | NO |
| 25 | `prh_rcp_type` | varchar(1) | NO |
| 26 | `prh_buyer` | varchar(12) | NO |
| 27 | `prh_crt_by` | varchar(12) | NO |
| 28 | `prh_crt_date` | datetime | NO |
| 29 | `prh_char1` | varchar(255) | NO |
| 30 | `prh_char2` | varchar(255) | NO |
| 31 | `prh_char3` | varchar(255) | NO |
| 32 | `prh_char4` | varchar(255) | NO |
| 33 | `prh_char5` | varchar(255) | NO |
| 34 | `prh_char6` | varchar(255) | NO |
| 35 | `prh_qty1` | decimal(19,8) | NO |
| 36 | `prh_qty2` | decimal(19,8) | NO |
| 37 | `prh_pt_desc` | varchar(255) | NO |
| 38 | `prh_dept` | varchar(10) | NO |
| 39 | `prh_src_nbr` | varchar(15) | NO |
| 40 | `prh_src_line` | int(10,0) | NO |

### `dbo.print_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `print_flow_no` | int(10,0) | NO |
| 2 | `print_prog` | varchar(12) | NO |
| 3 | `print_key1` | varchar(30) | NO |
| 4 | `print_key2` | varchar(30) | NO |
| 5 | `print_key3` | varchar(30) | NO |
| 6 | `print_key4` | varchar(30) | NO |
| 7 | `print_key5` | varchar(30) | NO |
| 8 | `print_key6` | varchar(30) | NO |
| 9 | `print_doc_crt_by` | varchar(12) | NO |
| 10 | `print_doc_crt_date` | datetime | NO |
| 11 | `print_by` | varchar(12) | NO |
| 12 | `print_date` | datetime | NO |
| 13 | `print_special` | bit | NO |
| 14 | `print_rmks` | varchar(255) | NO |
| 15 | `print_char1` | varchar(255) | NO |
| 16 | `print_char2` | varchar(255) | NO |
| 17 | `print_char3` | varchar(255) | NO |
| 18 | `print_char4` | varchar(255) | NO |
| 19 | `print_char5` | varchar(255) | NO |
| 20 | `print_char6` | varchar(255) | NO |
| 21 | `print_qty1` | decimal(19,8) | NO |
| 22 | `print_qty2` | decimal(19,8) | NO |
| 23 | `print_rpt_name` | varchar(30) | NO |

### `dbo.pro_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pro_site` | varchar(8) | NO |
| 2 | `pro_nbr` | varchar(15) | NO |
| 3 | `pro_date` | datetime | NO |
| 4 | `pro_rmks` | varchar(255) | NO |
| 5 | `pro_wf_status` | varchar(1) | NO |
| 6 | `pro_prog_code` | varchar(12) | NO |
| 7 | `pro_doc_code` | varchar(12) | NO |
| 8 | `pro_crt_by` | varchar(12) | NO |
| 9 | `pro_crt_date` | datetime | NO |
| 10 | `pro_mod_times` | int(10,0) | NO |
| 11 | `pro_mod_by` | varchar(12) | NO |
| 12 | `pro_mod_date` | datetime | NO |
| 13 | `pro_pst` | bit | NO |
| 14 | `pro_pst_by` | varchar(12) | NO |
| 15 | `pro_pst_date` | datetime | YES |
| 16 | `pro_char1` | varchar(255) | NO |
| 17 | `pro_char2` | varchar(255) | NO |
| 18 | `pro_char3` | varchar(255) | NO |
| 19 | `pro_char4` | varchar(255) | NO |
| 20 | `pro_char5` | varchar(255) | NO |
| 21 | `pro_char6` | varchar(255) | NO |
| 22 | `pro_qty1` | decimal(19,8) | NO |
| 23 | `pro_qty2` | decimal(19,8) | NO |

### `dbo.prod_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prod_nbr` | varchar(15) | NO |
| 2 | `prod_line` | int(10,0) | NO |
| 3 | `prod_plad_nbr` | varchar(15) | NO |
| 4 | `prod_plad_line` | int(10,0) | NO |
| 5 | `prod_log` | varchar(255) | NO |
| 6 | `prod_ove_sign` | varchar(1) | NO |
| 7 | `prod_sta_date` | datetime | YES |
| 8 | `prod_ove_date` | datetime | YES |
| 9 | `prod_days` | int(10,0) | NO |
| 10 | `prod_cmmt` | varchar(255) | NO |
| 11 | `prod_crt_by` | varchar(12) | NO |
| 12 | `prod_crt_date` | datetime | NO |
| 13 | `prod_mod_times` | int(10,0) | NO |
| 14 | `prod_mod_by` | varchar(12) | NO |
| 15 | `prod_mod_date` | datetime | NO |
| 16 | `prod_char1` | varchar(255) | NO |
| 17 | `prod_char2` | varchar(255) | NO |
| 18 | `prod_char3` | varchar(255) | NO |
| 19 | `prod_char4` | varchar(255) | NO |
| 20 | `prod_char5` | varchar(255) | NO |
| 21 | `prod_char6` | varchar(255) | NO |
| 22 | `prod_qty1` | decimal(19,8) | NO |
| 23 | `prod_qty2` | decimal(19,8) | NO |

### `dbo.ps_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ps_par` | varchar(30) | NO |
| 2 | `ps_comp` | varchar(30) | NO |
| 3 | `ps_start` | datetime | NO |
| 4 | `ps_end` | datetime | NO |
| 5 | `ps_qty_m` | numeric(19,8) | NO |
| 6 | `ps_qty_d` | numeric(19,8) | NO |
| 7 | `ps_op` | int(10,0) | NO |
| 8 | `ps_scrp_pct` | decimal(19,8) | NO |
| 9 | `ps_lt_off` | int(10,0) | NO |
| 10 | `ps_seq` | int(10,0) | NO |
| 11 | `ps_rmks` | varchar(255) | NO |
| 12 | `ps_end_ecn` | varchar(15) | NO |
| 13 | `ps_crt_by` | varchar(12) | NO |
| 14 | `ps_crt_date` | datetime | NO |
| 15 | `ps_mod_times` | int(10,0) | NO |
| 16 | `ps_mod_by` | varchar(12) | NO |
| 17 | `ps_mod_date` | datetime | NO |
| 18 | `ps_char1` | varchar(255) | NO |
| 19 | `ps_char2` | varchar(255) | NO |
| 20 | `ps_char3` | varchar(255) | NO |
| 21 | `ps_char4` | varchar(255) | NO |
| 22 | `ps_char5` | varchar(255) | NO |
| 23 | `ps_char6` | varchar(255) | NO |
| 24 | `ps_qty1` | decimal(19,8) | NO |
| 25 | `ps_qty2` | decimal(19,8) | NO |
| 26 | `ps_version` | varchar(10) | NO |
| 27 | `ps_desc` | varchar(255) | NO |
| 28 | `ps_spec` | varchar(255) | NO |
| 29 | `ps_um_eng` | varchar(4) | NO |
| 30 | `ps_vend` | varchar(8) | NO |
| 31 | `ps_curr` | varchar(4) | NO |
| 32 | `ps_vat` | decimal(19,8) | NO |
| 33 | `ps_pc_nbr` | varchar(15) | NO |
| 34 | `ps_pur_cost` | decimal(19,8) | NO |
| 35 | `ps_ord_min` | numeric(19,8) | NO |
| 36 | `ps_ord_mult` | numeric(19,8) | NO |
| 37 | `ps_mod_cost` | decimal(19,8) | NO |
| 38 | `ps_oth_cost` | decimal(19,8) | NO |

### `dbo.psdc_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `psdc_par` | varchar(30) | NO |
| 2 | `psdc_comp` | varchar(30) | NO |
| 3 | `psdc_start` | datetime | NO |
| 4 | `psdc_seq` | int(10,0) | NO |
| 5 | `psdc_depth_fr` | numeric(19,8) | NO |
| 6 | `psdc_label_fr` | varchar(255) | NO |
| 7 | `psdc_rmks_fr` | varchar(255) | NO |
| 8 | `psdc_depth_to` | numeric(19,8) | NO |
| 9 | `psdc_label_to` | varchar(255) | NO |
| 10 | `psdc_rmks_to` | varchar(255) | NO |
| 11 | `psdc_length` | numeric(19,8) | NO |
| 12 | `psdc_length_ex` | numeric(19,8) | NO |
| 13 | `psdc_qty` | numeric(19,8) | NO |
| 14 | `psdc_rmks` | varchar(255) | NO |
| 15 | `psdc_crt_by` | varchar(12) | NO |
| 16 | `psdc_crt_date` | datetime | NO |
| 17 | `psdc_mod_times` | int(10,0) | NO |
| 18 | `psdc_mod_by` | varchar(12) | NO |
| 19 | `psdc_mod_date` | datetime | NO |
| 20 | `psdc_char1` | varchar(255) | NO |
| 21 | `psdc_char2` | varchar(255) | NO |
| 22 | `psdc_char3` | varchar(255) | NO |
| 23 | `psdc_char4` | varchar(255) | NO |
| 24 | `psdc_char5` | varchar(255) | NO |
| 25 | `psdc_char6` | varchar(255) | NO |
| 26 | `psdc_qty1` | decimal(19,8) | NO |
| 27 | `psdc_qty2` | decimal(19,8) | NO |

### `dbo.psvd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `psvd_par` | varchar(30) | NO |
| 2 | `psvd_version` | varchar(10) | NO |
| 3 | `psvd_line` | int(10,0) | NO |
| 4 | `psvd_dept` | varchar(10) | NO |
| 5 | `psvd_seq` | int(10,0) | NO |
| 6 | `psvd_rmks` | varchar(255) | NO |
| 7 | `psvd_crt_by` | varchar(12) | NO |
| 8 | `psvd_crt_date` | datetime | NO |
| 9 | `psvd_mod_times` | int(10,0) | NO |
| 10 | `psvd_mod_by` | varchar(12) | NO |
| 11 | `psvd_mod_date` | datetime | NO |
| 12 | `psvd_pst` | bit | NO |
| 13 | `psvd_pst_by` | varchar(12) | NO |
| 14 | `psvd_pst_date` | datetime | YES |
| 15 | `psvd_char1` | varchar(255) | NO |
| 16 | `psvd_char2` | varchar(255) | NO |
| 17 | `psvd_char3` | varchar(255) | NO |
| 18 | `psvd_char4` | varchar(255) | NO |
| 19 | `psvd_char5` | varchar(255) | NO |
| 20 | `psvd_char6` | varchar(255) | NO |
| 21 | `psvd_qty1` | decimal(19,8) | NO |
| 22 | `psvd_qty2` | decimal(19,8) | NO |

### `dbo.pt_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pt_part` | varchar(30) | NO |
| 2 | `pt_desc1` | varchar(255) | NO |
| 3 | `pt_desc2` | varchar(255) | NO |
| 4 | `pt_custom_code` | varchar(50) | NO |
| 5 | `pt_barcode` | varchar(80) | NO |
| 6 | `pt_spec` | varchar(255) | NO |
| 7 | `pt_um` | varchar(4) | NO |
| 8 | `pt_prod_line` | varchar(4) | NO |
| 9 | `pt_added` | datetime | NO |
| 10 | `pt_part_type` | varchar(30) | NO |
| 11 | `pt_group` | varchar(30) | NO |
| 12 | `pt_draw` | varchar(18) | NO |
| 13 | `pt_picture` | varchar(255) | NO |
| 14 | `pt_rev` | varchar(4) | NO |
| 15 | `pt_status` | bit | NO |
| 16 | `pt_gross_weight` | numeric(19,8) | NO |
| 17 | `pt_net_weight` | numeric(19,8) | NO |
| 18 | `pt_case_qty` | numeric(19,8) | NO |
| 19 | `pt_scrp_pct` | decimal(19,8) | NO |
| 20 | `pt_ship_mark` | varchar(255) | NO |
| 21 | `pt_carton_l` | numeric(19,8) | NO |
| 22 | `pt_carton_w` | numeric(19,8) | NO |
| 23 | `pt_carton_h` | numeric(19,8) | NO |
| 24 | `pt_total` | numeric(19,8) | NO |
| 25 | `pt_um_eng` | varchar(4) | NO |
| 26 | `pt_um_eng_m` | decimal(19,8) | NO |
| 27 | `pt_um_eng_d` | decimal(19,8) | NO |
| 28 | `pt_um_pur` | varchar(4) | NO |
| 29 | `pt_um_pur_m` | decimal(19,8) | NO |
| 30 | `pt_um_pur_d` | decimal(19,8) | NO |
| 31 | `pt_um_sl` | varchar(4) | NO |
| 32 | `pt_um_sl_m` | decimal(19,8) | NO |
| 33 | `pt_um_sl_d` | decimal(19,8) | NO |
| 34 | `pt_um_isu` | varchar(4) | NO |
| 35 | `pt_um_isu_m` | decimal(19,8) | NO |
| 36 | `pt_um_isu_d` | decimal(19,8) | NO |
| 37 | `pt_abc` | varchar(1) | NO |
| 38 | `pt_loc` | varchar(8) | NO |
| 39 | `pt_cyc_int` | int(10,0) | NO |
| 40 | `pt_lot_serial` | bit | NO |
| 41 | `pt_lot_grp` | varchar(15) | NO |
| 42 | `pt_keeper` | varchar(12) | NO |
| 43 | `pt_shelf_life` | int(10,0) | NO |
| 44 | `pt_wo_line` | varchar(8) | NO |
| 45 | `pt_plan_ord` | bit | NO |
| 46 | `pt_time_fence` | int(10,0) | NO |
| 47 | `pt_ord_pol` | varchar(4) | NO |
| 48 | `pt_ord_qty` | numeric(19,8) | NO |
| 49 | `pt_ord_per` | int(10,0) | NO |
| 50 | `pt_sfty_stk` | numeric(19,8) | NO |
| 51 | `pt_rop` | numeric(19,8) | NO |
| 52 | `pt_buyer` | varchar(12) | NO |
| 53 | `pt_planner` | varchar(12) | NO |
| 54 | `pt_memo_item` | bit | NO |
| 55 | `pt_max_qty` | numeric(19,8) | NO |
| 56 | `pt_vend` | varchar(8) | NO |
| 57 | `pt_pm_code` | varchar(1) | NO |
| 58 | `pt_mfg_lt` | int(10,0) | NO |
| 59 | `pt_pur_lt` | int(10,0) | NO |
| 60 | `pt_insp_rqd` | bit | NO |
| 61 | `pt_gr_lt` | int(10,0) | NO |
| 62 | `pt_phantom` | bit | NO |
| 63 | `pt_ord_min` | numeric(19,8) | NO |
| 64 | `pt_ord_mult` | numeric(19,8) | NO |
| 65 | `pt_iss_batch` | numeric(19,8) | NO |
| 66 | `pt_roll_iss` | bit | NO |
| 67 | `pt_fgov_per` | decimal(19,8) | NO |
| 68 | `pt_iss_unlimit` | bit | NO |
| 69 | `pt_level` | int(10,0) | NO |
| 70 | `pt_wf_status` | varchar(1) | NO |
| 71 | `pt_crt_by` | varchar(12) | NO |
| 72 | `pt_crt_date` | datetime | NO |
| 73 | `pt_mod_times` | int(10,0) | NO |
| 74 | `pt_mod_by` | varchar(12) | NO |
| 75 | `pt_mod_date` | datetime | NO |
| 76 | `pt_pst` | bit | NO |
| 77 | `pt_pst_by` | varchar(12) | NO |
| 78 | `pt_pst_date` | datetime | YES |
| 79 | `pt_char1` | varchar(255) | NO |
| 80 | `pt_char2` | varchar(255) | NO |
| 81 | `pt_char3` | varchar(255) | NO |
| 82 | `pt_char4` | varchar(255) | NO |
| 83 | `pt_char5` | varchar(255) | NO |
| 84 | `pt_char6` | varchar(255) | NO |
| 85 | `pt_char7` | varchar(255) | NO |
| 86 | `pt_char8` | varchar(255) | NO |
| 87 | `pt_qty1` | decimal(19,8) | NO |
| 88 | `pt_qty2` | decimal(19,8) | NO |
| 89 | `pt_qty3` | decimal(19,8) | NO |
| 90 | `pt_qty4` | decimal(19,8) | NO |
| 91 | `pt_expu_perm` | bit | NO |
| 92 | `pt_exsl_perm` | bit | NO |
| 93 | `pt_loc_pos` | varchar(18) | NO |
| 94 | `pt_eng` | varchar(12) | NO |
| 95 | `pt_custom_name` | varchar(255) | NO |
| 96 | `pt_op` | int(10,0) | NO |
| 97 | `pt_backflush` | varchar(1) | NO |
| 98 | `pt_backflush_s` | varchar(1) | NO |
| 99 | `pt_sch_type` | varchar(30) | NO |
| 100 | `pt_ovr_unmrp` | bit | NO |

### `dbo.pt_mstrbase` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pt_part` | varchar(30) | NO |
| 2 | `pt_desc1` | varchar(255) | NO |
| 3 | `pt_desc2` | varchar(255) | NO |
| 4 | `pt_custom_code` | varchar(50) | NO |
| 5 | `pt_barcode` | varchar(80) | NO |
| 6 | `pt_spec` | varchar(255) | NO |
| 7 | `pt_um` | varchar(4) | NO |
| 8 | `pt_prod_line` | varchar(4) | NO |
| 9 | `pt_added` | datetime | NO |
| 10 | `pt_part_type` | varchar(30) | NO |
| 11 | `pt_group` | varchar(30) | NO |
| 12 | `pt_draw` | varchar(18) | NO |
| 13 | `pt_picture` | varchar(255) | NO |
| 14 | `pt_rev` | varchar(4) | NO |
| 15 | `pt_status` | bit | NO |
| 16 | `pt_gross_weight` | numeric(19,8) | NO |
| 17 | `pt_net_weight` | numeric(19,8) | NO |
| 18 | `pt_case_qty` | numeric(19,8) | NO |
| 19 | `pt_scrp_pct` | decimal(19,8) | NO |
| 20 | `pt_ship_mark` | varchar(255) | NO |
| 21 | `pt_carton_l` | numeric(19,8) | NO |
| 22 | `pt_carton_w` | numeric(19,8) | NO |
| 23 | `pt_carton_h` | numeric(19,8) | NO |
| 24 | `pt_total` | numeric(19,8) | NO |
| 25 | `pt_um_eng` | varchar(4) | NO |
| 26 | `pt_um_eng_m` | decimal(19,8) | NO |
| 27 | `pt_um_eng_d` | decimal(19,8) | NO |
| 28 | `pt_um_pur` | varchar(4) | NO |
| 29 | `pt_um_pur_m` | decimal(19,8) | NO |
| 30 | `pt_um_pur_d` | decimal(19,8) | NO |
| 31 | `pt_um_sl` | varchar(4) | NO |
| 32 | `pt_um_sl_m` | decimal(19,8) | NO |
| 33 | `pt_um_sl_d` | decimal(19,8) | NO |
| 34 | `pt_um_isu` | varchar(4) | NO |
| 35 | `pt_um_isu_m` | decimal(19,8) | NO |
| 36 | `pt_um_isu_d` | decimal(19,8) | NO |
| 37 | `pt_abc` | varchar(1) | NO |
| 38 | `pt_loc` | varchar(8) | NO |
| 39 | `pt_cyc_int` | int(10,0) | NO |
| 40 | `pt_lot_serial` | bit | NO |
| 41 | `pt_lot_grp` | varchar(15) | NO |
| 42 | `pt_keeper` | varchar(12) | NO |
| 43 | `pt_shelf_life` | int(10,0) | NO |
| 44 | `pt_wo_line` | varchar(8) | NO |
| 45 | `pt_plan_ord` | bit | NO |
| 46 | `pt_time_fence` | int(10,0) | NO |
| 47 | `pt_ord_pol` | varchar(4) | NO |
| 48 | `pt_ord_qty` | numeric(19,8) | NO |
| 49 | `pt_ord_per` | int(10,0) | NO |
| 50 | `pt_sfty_stk` | numeric(19,8) | NO |
| 51 | `pt_rop` | numeric(19,8) | NO |
| 52 | `pt_buyer` | varchar(12) | NO |
| 53 | `pt_planner` | varchar(12) | NO |
| 54 | `pt_memo_item` | bit | NO |
| 55 | `pt_max_qty` | numeric(19,8) | NO |
| 56 | `pt_vend` | varchar(8) | NO |
| 57 | `pt_pm_code` | varchar(1) | NO |
| 58 | `pt_mfg_lt` | int(10,0) | NO |
| 59 | `pt_pur_lt` | int(10,0) | NO |
| 60 | `pt_insp_rqd` | bit | NO |
| 61 | `pt_gr_lt` | int(10,0) | NO |
| 62 | `pt_phantom` | bit | NO |
| 63 | `pt_ord_min` | numeric(19,8) | NO |
| 64 | `pt_ord_mult` | numeric(19,8) | NO |
| 65 | `pt_iss_batch` | numeric(19,8) | NO |
| 66 | `pt_roll_iss` | bit | NO |
| 67 | `pt_fgov_per` | decimal(19,8) | NO |
| 68 | `pt_iss_unlimit` | bit | NO |
| 69 | `pt_level` | int(10,0) | NO |
| 70 | `pt_wf_status` | varchar(1) | NO |
| 71 | `pt_crt_by` | varchar(12) | NO |
| 72 | `pt_crt_date` | datetime | NO |
| 73 | `pt_mod_times` | int(10,0) | NO |
| 74 | `pt_mod_by` | varchar(12) | NO |
| 75 | `pt_mod_date` | datetime | NO |
| 76 | `pt_pst` | bit | NO |
| 77 | `pt_pst_by` | varchar(12) | NO |
| 78 | `pt_pst_date` | datetime | YES |
| 79 | `pt_char1` | varchar(255) | NO |
| 80 | `pt_char2` | varchar(255) | NO |
| 81 | `pt_char3` | varchar(255) | NO |
| 82 | `pt_char4` | varchar(255) | NO |
| 83 | `pt_char5` | varchar(255) | NO |
| 84 | `pt_char6` | varchar(255) | NO |
| 85 | `pt_char7` | varchar(255) | NO |
| 86 | `pt_char8` | varchar(255) | NO |
| 87 | `pt_qty1` | decimal(19,8) | NO |
| 88 | `pt_qty2` | decimal(19,8) | NO |
| 89 | `pt_qty3` | decimal(19,8) | NO |
| 90 | `pt_qty4` | decimal(19,8) | NO |
| 91 | `pt_expu_perm` | bit | NO |
| 92 | `pt_exsl_perm` | bit | NO |
| 93 | `pt_loc_pos` | varchar(18) | NO |
| 94 | `pt_eng` | varchar(12) | NO |
| 95 | `pt_custom_name` | varchar(255) | NO |
| 96 | `pt_op` | int(10,0) | NO |
| 97 | `pt_backflush` | varchar(1) | NO |
| 98 | `pt_backflush_s` | varchar(1) | NO |
| 99 | `pt_sch_type` | varchar(30) | NO |
| 100 | `pt_ovr_unmrp` | bit | NO |

### `dbo.pta_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pta_flow` | int(10,0) | NO |
| 2 | `pta_old` | varchar(30) | NO |
| 3 | `pta_new` | varchar(30) | NO |
| 4 | `pta_crt_by` | varchar(12) | NO |
| 5 | `pta_crt_date` | datetime | NO |

### `dbo.ptds_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptds_part` | varchar(30) | NO |
| 2 | `ptds_db` | varchar(30) | NO |
| 3 | `ptds_db_desc` | varchar(255) | NO |
| 4 | `ptds_sync` | bit | NO |
| 5 | `ptds_rmks` | varchar(255) | NO |
| 6 | `ptds_crt_by` | varchar(12) | NO |
| 7 | `ptds_crt_name` | varchar(30) | NO |
| 8 | `ptds_crt_date` | datetime | NO |
| 9 | `ptds_mod_times` | int(10,0) | NO |
| 10 | `ptds_mod_by` | varchar(12) | NO |
| 11 | `ptds_mod_name` | varchar(30) | NO |
| 12 | `ptds_mod_date` | datetime | NO |
| 13 | `ptds_char1` | varchar(255) | NO |
| 14 | `ptds_char2` | varchar(255) | NO |
| 15 | `ptds_char3` | varchar(255) | NO |
| 16 | `ptds_char4` | varchar(255) | NO |
| 17 | `ptds_char5` | varchar(255) | NO |
| 18 | `ptds_char6` | varchar(255) | NO |
| 19 | `ptds_qty1` | decimal(19,8) | NO |
| 20 | `ptds_qty2` | decimal(19,8) | NO |

### `dbo.ptp1_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp1_site` | varchar(8) | NO |
| 2 | `ptp1_part` | varchar(30) | NO |
| 3 | `ptp1_abc` | varchar(1) | NO |
| 4 | `ptp1_loc` | varchar(8) | NO |
| 5 | `ptp1_cyc_int` | int(10,0) | NO |
| 6 | `ptp1_lot_serial` | bit | NO |
| 7 | `ptp1_lot_grp` | varchar(15) | NO |
| 8 | `ptp1_keeper` | varchar(12) | NO |
| 9 | `ptp1_shelf_life` | int(10,0) | NO |
| 10 | `ptp1_crt_by` | varchar(12) | NO |
| 11 | `ptp1_crt_date` | datetime | NO |
| 12 | `ptp1_mod_times` | int(10,0) | NO |
| 13 | `ptp1_mod_by` | varchar(12) | NO |
| 14 | `ptp1_mod_date` | datetime | NO |
| 15 | `ptp1_char1` | varchar(255) | NO |
| 16 | `ptp1_char2` | varchar(255) | NO |
| 17 | `ptp1_char3` | varchar(255) | NO |
| 18 | `ptp1_char4` | varchar(255) | NO |
| 19 | `ptp1_char5` | varchar(255) | NO |
| 20 | `ptp1_char6` | varchar(255) | NO |
| 21 | `ptp1_qty1` | decimal(19,8) | NO |
| 22 | `ptp1_qty2` | decimal(19,8) | NO |

### `dbo.ptp2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp2_site` | varchar(8) | NO |
| 2 | `ptp2_part` | varchar(30) | NO |
| 3 | `ptp2_wo_line` | varchar(8) | NO |
| 4 | `ptp2_plan_ord` | bit | NO |
| 5 | `ptp2_time_fence` | int(10,0) | NO |
| 6 | `ptp2_ord_pol` | varchar(4) | NO |
| 7 | `ptp2_ord_qty` | numeric(19,8) | NO |
| 8 | `ptp2_ord_per` | int(10,0) | NO |
| 9 | `ptp2_sfty_stk` | numeric(19,8) | NO |
| 10 | `ptp2_rop` | numeric(19,8) | NO |
| 11 | `ptp2_buyer` | varchar(12) | NO |
| 12 | `ptp2_planner` | varchar(12) | NO |
| 13 | `ptp2_max_qty` | numeric(19,8) | NO |
| 14 | `ptp2_vend` | varchar(8) | NO |
| 15 | `ptp2_pm_code` | varchar(1) | NO |
| 16 | `ptp2_mfg_lt` | int(10,0) | NO |
| 17 | `ptp2_pur_lt` | int(10,0) | NO |
| 18 | `ptp2_insp_rqd` | bit | NO |
| 19 | `ptp2_gr_lt` | int(10,0) | NO |
| 20 | `ptp2_phantom` | bit | NO |
| 21 | `ptp2_ord_min` | numeric(19,8) | NO |
| 22 | `ptp2_ord_mult` | numeric(19,8) | NO |
| 23 | `ptp2_iss_batch` | numeric(19,8) | NO |
| 24 | `ptp2_roll_iss` | bit | NO |
| 25 | `ptp2_fgov_per` | decimal(19,8) | NO |
| 26 | `ptp2_iss_unlimit` | bit | NO |
| 27 | `ptp2_crt_by` | varchar(12) | NO |
| 28 | `ptp2_crt_date` | datetime | NO |
| 29 | `ptp2_mod_times` | int(10,0) | NO |
| 30 | `ptp2_mod_by` | varchar(12) | NO |
| 31 | `ptp2_mod_date` | datetime | NO |
| 32 | `ptp2_char1` | varchar(255) | NO |
| 33 | `ptp2_char2` | varchar(255) | NO |
| 34 | `ptp2_char3` | varchar(255) | NO |
| 35 | `ptp2_char4` | varchar(255) | NO |
| 36 | `ptp2_char5` | varchar(255) | NO |
| 37 | `ptp2_char6` | varchar(255) | NO |
| 38 | `ptp2_qty1` | decimal(19,8) | NO |
| 39 | `ptp2_qty2` | decimal(19,8) | NO |

### `dbo.ptp3_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp3_site` | varchar(8) | NO |
| 2 | `ptp3_part` | varchar(30) | NO |
| 3 | `ptp3_mtl_stdtl` | decimal(19,8) | NO |
| 4 | `ptp3_mtl_stdll` | decimal(19,8) | NO |
| 5 | `ptp3_lbr_stdtl` | decimal(19,8) | NO |
| 6 | `ptp3_lbr_stdll` | decimal(19,8) | NO |
| 7 | `ptp3_bdn_stdtl` | decimal(19,8) | NO |
| 8 | `ptp3_bdn_stdll` | decimal(19,8) | NO |
| 9 | `ptp3_sub_stdtl` | decimal(19,8) | NO |
| 10 | `ptp3_sub_stdll` | decimal(19,8) | NO |
| 11 | `ptp3_crt_by` | varchar(12) | NO |
| 12 | `ptp3_crt_date` | datetime | NO |
| 13 | `ptp3_mod_times` | int(10,0) | NO |
| 14 | `ptp3_mod_by` | varchar(12) | NO |
| 15 | `ptp3_mod_date` | datetime | NO |
| 16 | `ptp3_char1` | varchar(255) | NO |
| 17 | `ptp3_char2` | varchar(255) | NO |
| 18 | `ptp3_char3` | varchar(255) | NO |
| 19 | `ptp3_char4` | varchar(255) | NO |
| 20 | `ptp3_char5` | varchar(255) | NO |
| 21 | `ptp3_char6` | varchar(255) | NO |
| 22 | `ptp3_qty1` | decimal(19,8) | NO |
| 23 | `ptp3_qty2` | decimal(19,8) | NO |
| 24 | `ptp3_min_sod_price` | decimal(19,8) | NO |
| 25 | `ptp3_max_pur_cost` | decimal(19,8) | NO |

### `dbo.ptp3a_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp3a_site` | varchar(8) | NO |
| 2 | `ptp3a_part` | varchar(30) | NO |
| 3 | `ptp3a_start` | datetime | NO |
| 4 | `ptp3a_end` | datetime | NO |
| 5 | `ptp3a_sod_price` | decimal(19,8) | NO |
| 6 | `ptp3a_rmks` | varchar(255) | NO |
| 7 | `ptp3a_crt_by` | varchar(12) | NO |
| 8 | `ptp3a_crt_date` | datetime | NO |
| 9 | `ptp3a_mod_times` | int(10,0) | NO |
| 10 | `ptp3a_mod_by` | varchar(12) | NO |
| 11 | `ptp3a_mod_date` | datetime | NO |
| 12 | `ptp3a_char1` | varchar(255) | NO |
| 13 | `ptp3a_char2` | varchar(255) | NO |
| 14 | `ptp3a_char3` | varchar(255) | NO |
| 15 | `ptp3a_char4` | varchar(255) | NO |
| 16 | `ptp3a_char5` | varchar(255) | NO |
| 17 | `ptp3a_char6` | varchar(255) | NO |
| 18 | `ptp3a_qty1` | decimal(19,8) | NO |
| 19 | `ptp3a_qty2` | decimal(19,8) | NO |

### `dbo.ptp3b_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp3b_site` | varchar(8) | NO |
| 2 | `ptp3b_part` | varchar(30) | NO |
| 3 | `ptp3b_start` | datetime | NO |
| 4 | `ptp3b_cust` | varchar(8) | NO |
| 5 | `ptp3b_sod_price` | decimal(19,8) | NO |
| 6 | `ptp3b_rmks` | varchar(255) | NO |
| 7 | `ptp3b_crt_by` | varchar(12) | NO |
| 8 | `ptp3b_crt_date` | datetime | NO |
| 9 | `ptp3b_mod_times` | int(10,0) | NO |
| 10 | `ptp3b_mod_by` | varchar(12) | NO |
| 11 | `ptp3b_mod_date` | datetime | NO |
| 12 | `ptp3b_char1` | varchar(255) | NO |
| 13 | `ptp3b_char2` | varchar(255) | NO |
| 14 | `ptp3b_char3` | varchar(255) | NO |
| 15 | `ptp3b_char4` | varchar(255) | NO |
| 16 | `ptp3b_char5` | varchar(255) | NO |
| 17 | `ptp3b_char6` | varchar(255) | NO |
| 18 | `ptp3b_qty1` | decimal(19,8) | NO |
| 19 | `ptp3b_qty2` | decimal(19,8) | NO |

### `dbo.ptp3c_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp3c_site` | varchar(8) | NO |
| 2 | `ptp3c_part` | varchar(30) | NO |
| 3 | `ptp3c_start` | datetime | NO |
| 4 | `ptp3c_end` | datetime | NO |
| 5 | `ptp3c_pur_price` | decimal(19,8) | NO |
| 6 | `ptp3c_rmks` | varchar(255) | NO |
| 7 | `ptp3c_crt_by` | varchar(12) | NO |
| 8 | `ptp3c_crt_date` | datetime | NO |
| 9 | `ptp3c_mod_times` | int(10,0) | NO |
| 10 | `ptp3c_mod_by` | varchar(12) | NO |
| 11 | `ptp3c_mod_date` | datetime | NO |
| 12 | `ptp3c_char1` | varchar(255) | NO |
| 13 | `ptp3c_char2` | varchar(255) | NO |
| 14 | `ptp3c_char3` | varchar(255) | NO |
| 15 | `ptp3c_char4` | varchar(255) | NO |
| 16 | `ptp3c_char5` | varchar(255) | NO |
| 17 | `ptp3c_char6` | varchar(255) | NO |
| 18 | `ptp3c_qty1` | decimal(19,8) | NO |
| 19 | `ptp3c_qty2` | decimal(19,8) | NO |

### `dbo.ptp3d_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp3d_site` | varchar(8) | NO |
| 2 | `ptp3d_part` | varchar(30) | NO |
| 3 | `ptp3d_start` | datetime | NO |
| 4 | `ptp3d_vend` | varchar(8) | NO |
| 5 | `ptp3d_pur_price` | decimal(19,8) | NO |
| 6 | `ptp3d_rmks` | varchar(255) | NO |
| 7 | `ptp3d_crt_by` | varchar(12) | NO |
| 8 | `ptp3d_crt_date` | datetime | NO |
| 9 | `ptp3d_mod_times` | int(10,0) | NO |
| 10 | `ptp3d_mod_by` | varchar(12) | NO |
| 11 | `ptp3d_mod_date` | datetime | NO |
| 12 | `ptp3d_char1` | varchar(255) | NO |
| 13 | `ptp3d_char2` | varchar(255) | NO |
| 14 | `ptp3d_char3` | varchar(255) | NO |
| 15 | `ptp3d_char4` | varchar(255) | NO |
| 16 | `ptp3d_char5` | varchar(255) | NO |
| 17 | `ptp3d_char6` | varchar(255) | NO |
| 18 | `ptp3d_qty1` | decimal(19,8) | NO |
| 19 | `ptp3d_qty2` | decimal(19,8) | NO |

### `dbo.pts_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pts_par` | varchar(30) | NO |
| 2 | `pts_part` | varchar(30) | NO |
| 3 | `pts_sub_part` | varchar(30) | NO |
| 4 | `pts_start` | datetime | NO |
| 5 | `pts_end` | datetime | NO |
| 6 | `pts_qty_m` | numeric(19,8) | NO |
| 7 | `pts_qty_d` | numeric(19,8) | NO |
| 8 | `pts_priority` | int(10,0) | NO |
| 9 | `pts_rmks` | varchar(255) | NO |
| 10 | `pts_crt_by` | varchar(12) | NO |
| 11 | `pts_crt_date` | datetime | NO |
| 12 | `pts_mod_times` | int(10,0) | NO |
| 13 | `pts_mod_by` | varchar(12) | NO |
| 14 | `pts_mod_date` | datetime | NO |
| 15 | `pts_char1` | varchar(255) | NO |
| 16 | `pts_char2` | varchar(255) | NO |
| 17 | `pts_char3` | varchar(255) | NO |
| 18 | `pts_char4` | varchar(255) | NO |
| 19 | `pts_char5` | varchar(255) | NO |
| 20 | `pts_char6` | varchar(255) | NO |
| 21 | `pts_qty1` | decimal(19,8) | NO |
| 22 | `pts_qty2` | decimal(19,8) | NO |

### `dbo.ptss_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptss_nbr` | varchar(15) | NO |
| 2 | `ptss_date` | datetime | NO |
| 3 | `ptss_expire` | datetime | NO |
| 4 | `ptss_part` | varchar(30) | NO |
| 5 | `ptss_rmks` | varchar(255) | NO |
| 6 | `ptss_crt_by` | varchar(12) | NO |
| 7 | `ptss_crt_date` | datetime | NO |
| 8 | `ptss_mod_times` | int(10,0) | NO |
| 9 | `ptss_mod_by` | varchar(12) | NO |
| 10 | `ptss_mod_date` | datetime | NO |
| 11 | `ptss_pst` | bit | NO |
| 12 | `ptss_pst_by` | varchar(12) | NO |
| 13 | `ptss_pst_date` | datetime | YES |
| 14 | `ptss_char1` | varchar(255) | NO |
| 15 | `ptss_char2` | varchar(255) | NO |
| 16 | `ptss_char3` | varchar(255) | NO |
| 17 | `ptss_char4` | varchar(255) | NO |
| 18 | `ptss_char5` | varchar(255) | NO |
| 19 | `ptss_char6` | varchar(255) | NO |
| 20 | `ptss_qty1` | decimal(19,8) | NO |
| 21 | `ptss_qty2` | decimal(19,8) | NO |

### `dbo.ptssd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptssd_nbr` | varchar(15) | NO |
| 2 | `ptssd_line` | int(10,0) | NO |
| 3 | `ptssd_part` | varchar(30) | NO |
| 4 | `ptssd_seq` | int(10,0) | NO |
| 5 | `ptssd_rmks` | varchar(255) | NO |
| 6 | `ptssd_crt_by` | varchar(12) | NO |
| 7 | `ptssd_crt_date` | datetime | NO |
| 8 | `ptssd_mod_times` | int(10,0) | NO |
| 9 | `ptssd_mod_by` | varchar(12) | NO |
| 10 | `ptssd_mod_date` | datetime | NO |
| 11 | `ptssd_char1` | varchar(255) | NO |
| 12 | `ptssd_char2` | varchar(255) | NO |
| 13 | `ptssd_char3` | varchar(255) | NO |
| 14 | `ptssd_char4` | varchar(255) | NO |
| 15 | `ptssd_char5` | varchar(255) | NO |
| 16 | `ptssd_char6` | varchar(255) | NO |
| 17 | `ptssd_qty1` | decimal(19,8) | NO |
| 18 | `ptssd_qty2` | decimal(19,8) | NO |

### `dbo.qex_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `qex_nbr` | varchar(15) | NO |
| 2 | `qex_type` | varchar(1) | NO |
| 3 | `qex_start` | datetime | NO |
| 4 | `qex_end` | datetime | NO |
| 5 | `qex_rmks` | varchar(255) | NO |
| 6 | `qex_wf_status` | varchar(1) | NO |
| 7 | `qex_site` | varchar(8) | NO |
| 8 | `qex_prog_code` | varchar(12) | NO |
| 9 | `qex_doc_code` | varchar(12) | NO |
| 10 | `qex_crt_by` | varchar(12) | NO |
| 11 | `qex_crt_date` | datetime | NO |
| 12 | `qex_mod_times` | int(10,0) | NO |
| 13 | `qex_mod_by` | varchar(12) | NO |
| 14 | `qex_mod_date` | datetime | NO |
| 15 | `qex_pst` | bit | NO |
| 16 | `qex_pst_by` | varchar(12) | NO |
| 17 | `qex_pst_date` | datetime | YES |
| 18 | `qex_char1` | varchar(255) | NO |
| 19 | `qex_char2` | varchar(255) | NO |
| 20 | `qex_char3` | varchar(255) | NO |
| 21 | `qex_char4` | varchar(255) | NO |
| 22 | `qex_char5` | varchar(255) | NO |
| 23 | `qex_char6` | varchar(255) | NO |
| 24 | `qex_qty1` | decimal(19,8) | NO |
| 25 | `qex_qty2` | decimal(19,8) | NO |

### `dbo.qexd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `qexd_nbr` | varchar(15) | NO |
| 2 | `qexd_line` | int(10,0) | NO |
| 3 | `qexd_group` | varchar(30) | NO |
| 4 | `qexd_part` | varchar(30) | NO |
| 5 | `qexd_rmks` | varchar(255) | NO |
| 6 | `qexd_crt_by` | varchar(12) | NO |
| 7 | `qexd_crt_date` | datetime | NO |
| 8 | `qexd_mod_times` | int(10,0) | NO |
| 9 | `qexd_mod_by` | varchar(12) | NO |
| 10 | `qexd_mod_date` | datetime | NO |
| 11 | `qexd_char1` | varchar(255) | NO |
| 12 | `qexd_char2` | varchar(255) | NO |
| 13 | `qexd_char3` | varchar(255) | NO |
| 14 | `qexd_char4` | varchar(255) | NO |
| 15 | `qexd_char5` | varchar(255) | NO |
| 16 | `qexd_char6` | varchar(255) | NO |
| 17 | `qexd_qty1` | decimal(19,8) | NO |
| 18 | `qexd_qty2` | decimal(19,8) | NO |

### `dbo.qexq_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `qexq_nbr` | varchar(15) | NO |
| 2 | `qexq_line` | int(10,0) | NO |
| 3 | `qexq_qty_fr` | numeric(19,8) | NO |
| 4 | `qexq_qty_to` | numeric(19,8) | NO |
| 5 | `qexq_spare_type` | varchar(1) | NO |
| 6 | `qexq_spare_pct` | numeric(19,8) | NO |
| 7 | `qexq_spare_qty` | numeric(19,8) | NO |
| 8 | `qexq_spare_max` | numeric(19,8) | NO |
| 9 | `qexq_ex_type` | varchar(1) | NO |
| 10 | `qexq_ex_pct` | numeric(19,8) | NO |
| 11 | `qexq_ex_qty` | numeric(19,8) | NO |
| 12 | `qexq_ex_max` | numeric(19,8) | NO |
| 13 | `qexq_rmks` | varchar(255) | NO |
| 14 | `qexq_crt_by` | varchar(12) | NO |
| 15 | `qexq_crt_date` | datetime | NO |
| 16 | `qexq_mod_times` | int(10,0) | NO |
| 17 | `qexq_mod_by` | varchar(12) | NO |
| 18 | `qexq_mod_date` | datetime | NO |
| 19 | `qexq_char1` | varchar(255) | NO |
| 20 | `qexq_char2` | varchar(255) | NO |
| 21 | `qexq_char3` | varchar(255) | NO |
| 22 | `qexq_char4` | varchar(255) | NO |
| 23 | `qexq_char5` | varchar(255) | NO |
| 24 | `qexq_char6` | varchar(255) | NO |
| 25 | `qexq_qty1` | decimal(19,8) | NO |
| 26 | `qexq_qty2` | decimal(19,8) | NO |

### `dbo.qexv_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `qexv_nbr` | varchar(15) | NO |
| 2 | `qexv_addr` | varchar(8) | NO |
| 3 | `qexv_rmks` | varchar(255) | NO |
| 4 | `qexv_crt_by` | varchar(12) | NO |
| 5 | `qexv_crt_date` | datetime | NO |
| 6 | `qexv_mod_times` | int(10,0) | NO |
| 7 | `qexv_mod_by` | varchar(12) | NO |
| 8 | `qexv_mod_date` | datetime | NO |
| 9 | `qexv_char1` | varchar(255) | NO |
| 10 | `qexv_char2` | varchar(255) | NO |
| 11 | `qexv_char3` | varchar(255) | NO |
| 12 | `qexv_char4` | varchar(255) | NO |
| 13 | `qexv_char5` | varchar(255) | NO |
| 14 | `qexv_char6` | varchar(255) | NO |
| 15 | `qexv_qty1` | decimal(19,8) | NO |
| 16 | `qexv_qty2` | decimal(19,8) | NO |

### `dbo.req_auto` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `auto_user` | varchar(12) | NO |
| 2 | `auto_flow` | int(10,0) | NO |
| 3 | `auto_selected` | bit | NO |
| 4 | `auto_vend` | varchar(8) | NO |
| 5 | `auto_curr` | varchar(4) | NO |
| 6 | `auto_vat` | decimal(19,8) | NO |
| 7 | `auto_need` | datetime | NO |
| 8 | `auto_pr_rel_date` | datetime | NO |
| 9 | `auto_req_pr_nbr` | varchar(15) | NO |
| 10 | `auto_req_line` | int(10,0) | NO |
| 11 | `auto_pr_req_by` | varchar(12) | NO |
| 12 | `auto_req_part` | varchar(30) | NO |
| 13 | `auto_req_qty` | numeric(19,8) | NO |
| 14 | `auto_req_pt_desc` | varchar(255) | NO |
| 15 | `auto_pr_dept` | varchar(10) | NO |
| 16 | `auto_req_um` | varchar(4) | NO |
| 17 | `auto_price` | decimal(19,8) | NO |
| 18 | `auto_um_pur` | varchar(4) | NO |
| 19 | `auto_um_pur_m` | numeric(19,8) | NO |
| 20 | `auto_um_pur_d` | numeric(19,8) | NO |
| 21 | `auto_vend_part` | varchar(30) | NO |
| 22 | `auto_pr_rmks` | varchar(255) | NO |
| 23 | `auto_req_rmks` | varchar(255) | NO |
| 24 | `auto_req_wo_nbr` | varchar(15) | NO |
| 25 | `auto_req_wo_lot` | varchar(18) | NO |
| 26 | `auto_req_so_nbr` | varchar(15) | NO |
| 27 | `auto_req_so_line` | int(10,0) | NO |
| 28 | `auto_ord_min` | numeric(19,8) | NO |
| 29 | `auto_ord_mult` | numeric(19,8) | NO |
| 30 | `auto_iss_batch` | numeric(19,8) | NO |
| 31 | `auto_qty_per` | numeric(19,8) | NO |
| 32 | `auto_days_per` | int(10,0) | NO |

### `dbo.req_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `req_pr_nbr` | varchar(15) | NO |
| 2 | `req_line` | int(10,0) | NO |
| 3 | `req_src` | varchar(1) | NO |
| 4 | `req_part` | varchar(30) | NO |
| 5 | `req_pt_desc` | varchar(255) | NO |
| 6 | `req_um` | varchar(4) | NO |
| 7 | `req_need` | datetime | NO |
| 8 | `req_qty` | numeric(19,8) | NO |
| 9 | `req_qty_applied` | numeric(19,8) | NO |
| 10 | `req_wo_nbr` | varchar(15) | NO |
| 11 | `req_wo_lot` | varchar(18) | NO |
| 12 | `req_status` | varchar(1) | NO |
| 13 | `req_close_by` | varchar(12) | NO |
| 14 | `req_close_date` | datetime | YES |
| 15 | `req_rmks` | varchar(255) | NO |
| 16 | `req_crt_by` | varchar(12) | NO |
| 17 | `req_crt_date` | datetime | NO |
| 18 | `req_mod_times` | int(10,0) | NO |
| 19 | `req_mod_by` | varchar(12) | NO |
| 20 | `req_mod_date` | datetime | NO |
| 21 | `req_char1` | varchar(255) | NO |
| 22 | `req_char2` | varchar(255) | NO |
| 23 | `req_char3` | varchar(255) | NO |
| 24 | `req_char4` | varchar(255) | NO |
| 25 | `req_char5` | varchar(255) | NO |
| 26 | `req_char6` | varchar(255) | NO |
| 27 | `req_qty1` | decimal(19,8) | NO |
| 28 | `req_qty2` | decimal(19,8) | NO |
| 29 | `req_mrp_req_self` | numeric(19,8) | NO |
| 30 | `req_mrp_req_tot` | numeric(19,8) | NO |
| 31 | `req_mrp_ld_net` | numeric(19,8) | NO |
| 32 | `req_mrp_ld_unnet` | numeric(19,8) | NO |
| 33 | `req_mrp_ord` | numeric(19,8) | NO |
| 34 | `req_mrp_pr` | numeric(19,8) | NO |
| 35 | `req_mrp_safe` | numeric(19,8) | NO |
| 36 | `req_mrp_alloc` | numeric(19,8) | NO |
| 37 | `req_mrp_left` | numeric(19,8) | NO |
| 38 | `req_mrp_short` | numeric(19,8) | NO |
| 39 | `req_mrp_qty_org` | numeric(19,8) | NO |
| 40 | `req_so_nbr` | varchar(15) | NO |
| 41 | `req_so_line` | int(10,0) | NO |
| 42 | `req_close_reason` | varchar(255) | NO |

### `dbo.reqd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `reqd_pr_nbr` | varchar(15) | NO |
| 2 | `reqd_req_line` | int(10,0) | NO |
| 3 | `reqd_line` | int(10,0) | NO |
| 4 | `reqd_wod_nbr` | varchar(15) | NO |
| 5 | `reqd_wod_lot` | varchar(18) | NO |
| 6 | `reqd_wod_seq` | int(10,0) | NO |
| 7 | `reqd_wod_part` | varchar(30) | NO |
| 8 | `reqd_wo_qty_ord` | numeric(19,8) | NO |
| 9 | `reqd_wod_qty_req_std` | numeric(19,8) | NO |
| 10 | `reqd_wod_qty_req_scr` | numeric(19,8) | NO |
| 11 | `reqd_wod_qty_req` | numeric(19,8) | NO |
| 12 | `reqd_pr_qty` | numeric(19,8) | NO |
| 13 | `reqd_char1` | varchar(255) | NO |
| 14 | `reqd_char2` | varchar(255) | NO |
| 15 | `reqd_char3` | varchar(255) | NO |
| 16 | `reqd_char4` | varchar(255) | NO |
| 17 | `reqd_char5` | varchar(255) | NO |
| 18 | `reqd_char6` | varchar(255) | NO |
| 19 | `reqd_qty1` | decimal(19,8) | NO |
| 20 | `reqd_qty2` | decimal(19,8) | NO |
| 21 | `reqd_mrp_req_tot` | numeric(19,8) | NO |
| 22 | `reqd_mrp_ld_net` | numeric(19,8) | NO |
| 23 | `reqd_mrp_ord` | numeric(19,8) | NO |
| 24 | `reqd_mrp_pr` | numeric(19,8) | NO |
| 25 | `reqd_mrp_safe` | numeric(19,8) | NO |
| 26 | `reqd_mrp_alloc` | numeric(19,8) | NO |
| 27 | `reqd_mrp_left` | numeric(19,8) | NO |
| 28 | `reqd_mrp_short` | numeric(19,8) | NO |
| 29 | `reqd_mrp_qty_org` | numeric(19,8) | NO |

### `dbo.ro_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ro_routing` | varchar(30) | NO |
| 2 | `ro_op` | int(10,0) | NO |
| 3 | `ro_start` | datetime | NO |
| 4 | `ro_end` | datetime | NO |
| 5 | `ro_wkctr` | varchar(8) | NO |
| 6 | `ro_desc` | varchar(100) | NO |
| 7 | `ro_um` | varchar(1) | NO |
| 8 | `ro_run` | numeric(19,8) | NO |
| 9 | `ro_prod_rate` | numeric(19,8) | NO |
| 10 | `ro_yield_pct` | decimal(19,8) | NO |
| 11 | `ro_vend` | varchar(8) | NO |
| 12 | `ro_tool` | varchar(80) | NO |
| 13 | `ro_param` | varchar(255) | NO |
| 14 | `ro_rmks` | varchar(255) | NO |
| 15 | `ro_crt_by` | varchar(12) | NO |
| 16 | `ro_crt_date` | datetime | NO |
| 17 | `ro_mod_times` | int(10,0) | NO |
| 18 | `ro_mod_by` | varchar(12) | NO |
| 19 | `ro_mod_date` | datetime | NO |
| 20 | `ro_char1` | varchar(255) | NO |
| 21 | `ro_char2` | varchar(255) | NO |
| 22 | `ro_char3` | varchar(255) | NO |
| 23 | `ro_char4` | varchar(255) | NO |
| 24 | `ro_char5` | varchar(255) | NO |
| 25 | `ro_char6` | varchar(255) | NO |
| 26 | `ro_qty1` | decimal(19,8) | NO |
| 27 | `ro_qty2` | decimal(19,8) | NO |
| 28 | `ro_um_rate` | numeric(19,8) | NO |
| 29 | `ro_default` | bit | NO |
| 30 | `ro_alt` | bit | NO |
| 31 | `ro_alt_op` | int(10,0) | NO |
| 32 | `ro_s_price` | decimal(19,8) | NO |
| 33 | `ro_type` | varchar(1) | NO |
| 34 | `ro_po_part` | varchar(30) | NO |

### `dbo.rts_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `rts_rts` | varchar(15) | NO |
| 2 | `rts_date` | datetime | NO |
| 3 | `rts_type` | varchar(1) | NO |
| 4 | `rts_vend` | varchar(8) | NO |
| 5 | `rts_curr` | varchar(4) | NO |
| 6 | `rts_ex_rate` | decimal(19,8) | NO |
| 7 | `rts_vat` | decimal(19,8) | NO |
| 8 | `rts_replace` | bit | NO |
| 9 | `rts_loc` | varchar(8) | NO |
| 10 | `rts_rmks` | varchar(255) | NO |
| 11 | `rts_wf_status` | varchar(1) | NO |
| 12 | `rts_site` | varchar(8) | NO |
| 13 | `rts_prog_code` | varchar(12) | NO |
| 14 | `rts_doc_code` | varchar(12) | NO |
| 15 | `rts_crt_by` | varchar(12) | NO |
| 16 | `rts_crt_date` | datetime | NO |
| 17 | `rts_mod_times` | int(10,0) | NO |
| 18 | `rts_mod_by` | varchar(12) | NO |
| 19 | `rts_mod_date` | datetime | NO |
| 20 | `rts_pst` | bit | NO |
| 21 | `rts_pst_by` | varchar(12) | NO |
| 22 | `rts_pst_date` | datetime | YES |
| 23 | `rts_char1` | varchar(255) | NO |
| 24 | `rts_char2` | varchar(255) | NO |
| 25 | `rts_char3` | varchar(255) | NO |
| 26 | `rts_char4` | varchar(255) | NO |
| 27 | `rts_char5` | varchar(255) | NO |
| 28 | `rts_char6` | varchar(255) | NO |
| 29 | `rts_qty1` | decimal(19,8) | NO |
| 30 | `rts_qty2` | decimal(19,8) | NO |
| 31 | `rts_data_src` | varchar(1) | NO |
| 32 | `rts_data_id` | varchar(255) | NO |
| 33 | `rts_src_nbr` | varchar(15) | NO |
| 34 | `rts_chk` | bit | NO |
| 35 | `rts_chk_by` | varchar(12) | NO |
| 36 | `rts_chk_date` | datetime | YES |
| 37 | `rts_src` | varchar(2) | NO |
| 38 | `rts_src_lot` | varchar(18) | NO |

### `dbo.rtsd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `rtsd_rts` | varchar(15) | NO |
| 2 | `rtsd_line` | int(10,0) | NO |
| 3 | `rtsd_po` | varchar(15) | NO |
| 4 | `rtsd_po_line` | int(10,0) | NO |
| 5 | `rtsd_part` | varchar(30) | NO |
| 6 | `rtsd_qty` | numeric(19,8) | NO |
| 7 | `rtsd_qty_spare` | numeric(19,8) | NO |
| 8 | `rtsd_loc` | varchar(8) | NO |
| 9 | `rtsd_lot` | varchar(18) | NO |
| 10 | `rtsd_um` | varchar(4) | NO |
| 11 | `rtsd_um_rate_m` | decimal(19,8) | NO |
| 12 | `rtsd_um_rate_d` | decimal(19,8) | NO |
| 13 | `rtsd_price` | decimal(19,8) | NO |
| 14 | `rtsd_rmks` | varchar(255) | NO |
| 15 | `rtsd_crt_by` | varchar(12) | NO |
| 16 | `rtsd_crt_date` | datetime | NO |
| 17 | `rtsd_mod_times` | int(10,0) | NO |
| 18 | `rtsd_mod_by` | varchar(12) | NO |
| 19 | `rtsd_mod_date` | datetime | NO |
| 20 | `rtsd_char1` | varchar(255) | NO |
| 21 | `rtsd_char2` | varchar(255) | NO |
| 22 | `rtsd_char3` | varchar(255) | NO |
| 23 | `rtsd_char4` | varchar(255) | NO |
| 24 | `rtsd_char5` | varchar(255) | NO |
| 25 | `rtsd_char6` | varchar(255) | NO |
| 26 | `rtsd_qty1` | decimal(19,8) | NO |
| 27 | `rtsd_qty2` | decimal(19,8) | NO |
| 28 | `rtsd_qty_inv` | numeric(19,8) | NO |
| 29 | `rtsd_qty_spare_inv` | numeric(19,8) | NO |
| 30 | `rtsd_data_src` | varchar(1) | NO |
| 31 | `rtsd_data_id` | varchar(255) | NO |
| 32 | `rtsd_src_nbr` | varchar(15) | NO |
| 33 | `rtsd_src_line` | int(10,0) | NO |
| 34 | `rtsd_replace` | bit | NO |
| 35 | `rtsd_fee` | bit | NO |
| 36 | `rtsd_src` | varchar(1) | NO |
| 37 | `rtsd_wip` | varchar(8) | NO |

### `dbo.rtsdd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `rtsdd_rts` | varchar(15) | NO |
| 2 | `rtsdd_line` | int(10,0) | NO |
| 3 | `rtsdd_seq` | int(10,0) | NO |
| 4 | `rtsdd_wod_seq` | int(10,0) | NO |
| 5 | `rtsdd_part` | varchar(30) | NO |
| 6 | `rtsdd_per_m` | numeric(19,8) | NO |
| 7 | `rtsdd_per_d` | numeric(19,8) | NO |
| 8 | `rtsdd_qty_req` | numeric(19,8) | NO |
| 9 | `rtsdd_vend` | varchar(8) | NO |
| 10 | `rtsdd_no_po` | bit | NO |
| 11 | `rtsdd_po` | varchar(15) | NO |
| 12 | `rtsdd_po_line` | int(10,0) | NO |
| 13 | `rtsdd_curr` | varchar(4) | NO |
| 14 | `rtsdd_vat` | numeric(19,8) | NO |
| 15 | `rtsdd_qty_rtn` | numeric(19,8) | NO |
| 16 | `rtsdd_left_back` | bit | NO |
| 17 | `rtsdd_qty_back` | numeric(19,8) | NO |
| 18 | `rtsdd_left_loc` | varchar(8) | NO |
| 19 | `rtsdd_lot` | varchar(18) | NO |
| 20 | `rtsdd_um` | varchar(4) | NO |
| 21 | `rtsdd_um_rate_m` | numeric(19,8) | NO |
| 22 | `rtsdd_um_rate_d` | numeric(19,8) | NO |
| 23 | `rtsdd_price` | numeric(19,8) | NO |
| 24 | `rtsdd_fee_amt` | numeric(19,8) | NO |
| 25 | `rtsdd_fee_price` | numeric(19,8) | NO |
| 26 | `rtsdd_replace` | bit | NO |
| 27 | `rtsdd_rmks` | varchar(255) | NO |
| 28 | `rtsdd_crt_by` | varchar(12) | NO |
| 29 | `rtsdd_crt_date` | datetime | NO |
| 30 | `rtsdd_mod_times` | int(10,0) | NO |
| 31 | `rtsdd_mod_by` | varchar(12) | NO |
| 32 | `rtsdd_mod_date` | datetime | NO |
| 33 | `rtsdd_char1` | varchar(255) | NO |
| 34 | `rtsdd_char2` | varchar(255) | NO |
| 35 | `rtsdd_char3` | varchar(255) | NO |
| 36 | `rtsdd_char4` | varchar(255) | NO |
| 37 | `rtsdd_char5` | varchar(255) | NO |
| 38 | `rtsdd_char6` | varchar(255) | NO |
| 39 | `rtsdd_qty1` | decimal(19,8) | NO |
| 40 | `rtsdd_qty2` | decimal(19,8) | NO |

### `dbo.sc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sc_nbr` | varchar(15) | NO |
| 2 | `sc_cust` | varchar(8) | NO |
| 3 | `sc_curr` | varchar(4) | NO |
| 4 | `sc_part` | varchar(30) | NO |
| 5 | `sc_cust_part` | varchar(80) | NO |
| 6 | `sc_um` | varchar(4) | NO |
| 7 | `sc_um_rate_m` | decimal(19,8) | NO |
| 8 | `sc_um_rate_d` | decimal(19,8) | NO |
| 9 | `sc_start` | datetime | NO |
| 10 | `sc_expire` | datetime | NO |
| 11 | `sc_vat` | bit | NO |
| 12 | `sc_vat_rate` | decimal(19,8) | NO |
| 13 | `sc_disc` | decimal(19,8) | NO |
| 14 | `sc_price` | decimal(19,8) | NO |
| 15 | `sc_rmks` | varchar(255) | NO |
| 16 | `sc_crt_by` | varchar(12) | NO |
| 17 | `sc_crt_date` | datetime | NO |
| 18 | `sc_wf_status` | varchar(1) | NO |
| 19 | `sc_mod_times` | int(10,0) | NO |
| 20 | `sc_mod_by` | varchar(12) | NO |
| 21 | `sc_mod_date` | datetime | NO |
| 22 | `sc_pst` | bit | NO |
| 23 | `sc_pst_by` | varchar(12) | NO |
| 24 | `sc_pst_date` | datetime | YES |
| 25 | `sc_char1` | varchar(255) | NO |
| 26 | `sc_char2` | varchar(255) | NO |
| 27 | `sc_char3` | varchar(255) | NO |
| 28 | `sc_char4` | varchar(255) | NO |
| 29 | `sc_char5` | varchar(255) | NO |
| 30 | `sc_char6` | varchar(255) | NO |
| 31 | `sc_qty1` | decimal(19,8) | NO |
| 32 | `sc_qty2` | decimal(19,8) | NO |
| 33 | `sc_ast_code` | varchar(15) | NO |
| 34 | `sc_spare_pct` | decimal(19,8) | NO |
| 35 | `sc_data_src` | varchar(1) | NO |
| 36 | `sc_data_id` | varchar(255) | NO |
| 37 | `sc_prog_code` | varchar(12) | NO |
| 38 | `sc_qtype` | varchar(2) | NO |
| 39 | `sc_cu_area` | varchar(30) | NO |
| 40 | `sc_cu_curr` | varchar(30) | NO |
| 41 | `sc_price_type` | varchar(1) | NO |
| 42 | `sc_prop1` | varchar(30) | NO |
| 43 | `sc_prop2` | varchar(30) | NO |
| 44 | `sc_prop3` | varchar(30) | NO |
| 45 | `sc_prop4` | varchar(30) | NO |
| 46 | `sc_chk` | bit | NO |
| 47 | `sc_chk_by` | varchar(12) | NO |
| 48 | `sc_chk_date` | datetime | YES |
| 49 | `sc_appro` | bit | NO |
| 50 | `sc_appro_by` | varchar(12) | NO |
| 51 | `sc_appro_date` | datetime | YES |

### `dbo.scrp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `scrp_par` | varchar(30) | NO |
| 2 | `scrp_key_item` | varchar(30) | NO |
| 3 | `scrp_pt_fr` | varchar(30) | NO |
| 4 | `scrp_pt_to` | varchar(30) | NO |
| 5 | `scrp_level1` | numeric(19,8) | NO |
| 6 | `scrp_rate1` | decimal(19,8) | NO |
| 7 | `scrp_sc_qty1` | numeric(19,8) | NO |
| 8 | `scrp_level2` | numeric(19,8) | NO |
| 9 | `scrp_rate2` | decimal(19,8) | NO |
| 10 | `scrp_sc_qty2` | numeric(19,8) | NO |
| 11 | `scrp_level3` | numeric(19,8) | NO |
| 12 | `scrp_rate3` | decimal(19,8) | NO |
| 13 | `scrp_sc_qty3` | numeric(19,8) | NO |
| 14 | `scrp_level4` | numeric(19,8) | NO |
| 15 | `scrp_rate4` | decimal(19,8) | NO |
| 16 | `scrp_sc_qty4` | numeric(19,8) | NO |
| 17 | `scrp_level5` | numeric(19,8) | NO |
| 18 | `scrp_rate5` | decimal(19,8) | NO |
| 19 | `scrp_sc_qty5` | numeric(19,8) | NO |
| 20 | `scrp_rmks` | varchar(255) | NO |
| 21 | `scrp_crt_by` | varchar(12) | NO |
| 22 | `scrp_crt_date` | datetime | NO |
| 23 | `scrp_mod_times` | int(10,0) | NO |
| 24 | `scrp_mod_by` | varchar(12) | NO |
| 25 | `scrp_mod_date` | datetime | NO |
| 26 | `scrp_char1` | varchar(255) | NO |
| 27 | `scrp_char2` | varchar(255) | NO |
| 28 | `scrp_char3` | varchar(255) | NO |
| 29 | `scrp_char4` | varchar(255) | NO |
| 30 | `scrp_char5` | varchar(255) | NO |
| 31 | `scrp_char6` | varchar(255) | NO |
| 32 | `scrp_qty1` | decimal(19,8) | NO |
| 33 | `scrp_qty2` | decimal(19,8) | NO |

### `dbo.sdh_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_flow_no` | int(10,0) | NO |
| 2 | `sdh_site` | varchar(8) | NO |
| 3 | `sdh_so_nbr` | varchar(15) | NO |
| 4 | `sdh_sod_line` | int(10,0) | NO |
| 5 | `sdh_dn_dn` | varchar(15) | NO |
| 6 | `sdh_dnd_line` | int(10,0) | NO |
| 7 | `sdh_dn_date` | datetime | NO |
| 8 | `sdh_ord_date` | datetime | YES |
| 9 | `sdh_cust` | varchar(8) | NO |
| 10 | `sdh_part` | varchar(30) | NO |
| 11 | `sdh_qty_ord` | numeric(19,8) | NO |
| 12 | `sdh_qty_spare` | numeric(19,8) | NO |
| 13 | `sdh_qty_shp` | numeric(19,8) | NO |
| 14 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 15 | `sdh_um` | varchar(4) | NO |
| 16 | `sdh_um_rate_m` | decimal(19,8) | NO |
| 17 | `sdh_um_rate_d` | decimal(19,8) | NO |
| 18 | `sdh_sod_price` | decimal(19,8) | NO |
| 19 | `sdh_curr` | varchar(4) | NO |
| 20 | `sdh_ex_rate` | decimal(19,8) | NO |
| 21 | `sdh_so_vat` | decimal(19,8) | NO |
| 22 | `sdh_dn_type` | varchar(1) | NO |
| 23 | `sdh_so_slspsn` | varchar(12) | NO |
| 24 | `sdh_cost` | decimal(19,8) | NO |
| 25 | `sdh_crt_by` | varchar(12) | NO |
| 26 | `sdh_crt_date` | datetime | NO |
| 27 | `sdh_char1` | varchar(255) | NO |
| 28 | `sdh_char2` | varchar(255) | NO |
| 29 | `sdh_char3` | varchar(255) | NO |
| 30 | `sdh_char4` | varchar(255) | NO |
| 31 | `sdh_char5` | varchar(255) | NO |
| 32 | `sdh_char6` | varchar(255) | NO |
| 33 | `sdh_qty1` | decimal(19,8) | NO |
| 34 | `sdh_qty2` | decimal(19,8) | NO |

### `dbo.shop_cal` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `shop_site` | varchar(8) | NO |
| 2 | `shop_wkctr` | varchar(8) | NO |
| 3 | `shop_mch` | varchar(8) | NO |
| 4 | `shop_wday1` | bit | NO |
| 5 | `shop_wday2` | bit | NO |
| 6 | `shop_wday3` | bit | NO |
| 7 | `shop_wday4` | bit | NO |
| 8 | `shop_wday5` | bit | NO |
| 9 | `shop_wday6` | bit | NO |
| 10 | `shop_wday7` | bit | NO |
| 11 | `shop_hour1` | decimal(19,8) | NO |
| 12 | `shop_hour2` | decimal(19,8) | NO |
| 13 | `shop_hour3` | decimal(19,8) | NO |
| 14 | `shop_hour4` | decimal(19,8) | NO |
| 15 | `shop_hour5` | decimal(19,8) | NO |
| 16 | `shop_hour6` | decimal(19,8) | NO |
| 17 | `shop_hour7` | decimal(19,8) | NO |
| 18 | `shop_crt_by` | varchar(12) | NO |
| 19 | `shop_crt_date` | datetime | NO |
| 20 | `shop_char1` | varchar(255) | NO |
| 21 | `shop_char2` | varchar(255) | NO |
| 22 | `shop_char3` | varchar(255) | NO |
| 23 | `shop_char4` | varchar(255) | NO |
| 24 | `shop_char5` | varchar(255) | NO |
| 25 | `shop_char6` | varchar(255) | NO |
| 26 | `shop_qty1` | decimal(19,8) | NO |
| 27 | `shop_qty2` | decimal(19,8) | NO |

### `dbo.si_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `si_site` | varchar(8) | NO |
| 2 | `si_desc` | varchar(50) | NO |
| 3 | `si_company` | varchar(8) | NO |
| 4 | `si_crt_by` | varchar(12) | NO |
| 5 | `si_crt_date` | datetime | NO |
| 6 | `si_char1` | varchar(255) | NO |
| 7 | `si_char2` | varchar(255) | NO |
| 8 | `si_char3` | varchar(255) | NO |
| 9 | `si_char4` | varchar(255) | NO |
| 10 | `si_char5` | varchar(255) | NO |
| 11 | `si_char6` | varchar(255) | NO |
| 12 | `si_qty1` | decimal(19,8) | NO |
| 13 | `si_qty2` | decimal(19,8) | NO |

### `dbo.so_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `so_nbr` | varchar(15) | NO |
| 2 | `so_cust` | varchar(8) | NO |
| 3 | `so_addr` | varchar(255) | NO |
| 4 | `so_ord_date` | datetime | NO |
| 5 | `so_po` | varchar(255) | NO |
| 6 | `so_cr_terms` | varchar(10) | NO |
| 7 | `so_slspsn` | varchar(12) | NO |
| 8 | `so_curr` | varchar(4) | NO |
| 9 | `so_ex_rate` | decimal(19,8) | NO |
| 10 | `so_vat` | decimal(19,8) | NO |
| 11 | `so_rev` | varchar(4) | NO |
| 12 | `so_site` | varchar(8) | NO |
| 13 | `so_prog_code` | varchar(12) | NO |
| 14 | `so_doc_type` | varchar(12) | NO |
| 15 | `so_consume` | bit | NO |
| 16 | `so_fc_nbr` | varchar(15) | NO |
| 17 | `so_consignment` | bit | NO |
| 18 | `so_rmks` | varchar(255) | NO |
| 19 | `so_terms` | text(2147483647) | YES |
| 20 | `so_wf_status` | varchar(1) | NO |
| 21 | `so_crt_by` | varchar(12) | NO |
| 22 | `so_crt_date` | datetime | NO |
| 23 | `so_mod_times` | int(10,0) | NO |
| 24 | `so_mod_by` | varchar(12) | NO |
| 25 | `so_mod_date` | datetime | NO |
| 26 | `so_pst` | bit | NO |
| 27 | `so_pst_by` | varchar(12) | NO |
| 28 | `so_pst_date` | datetime | YES |
| 29 | `so_chk` | bit | NO |
| 30 | `so_chk_by` | varchar(12) | NO |
| 31 | `so_chk_date` | datetime | YES |
| 32 | `so_char1` | varchar(255) | NO |
| 33 | `so_char2` | varchar(255) | NO |
| 34 | `so_char3` | varchar(255) | NO |
| 35 | `so_char4` | varchar(255) | NO |
| 36 | `so_char5` | varchar(255) | NO |
| 37 | `so_char6` | varchar(255) | NO |
| 38 | `so_qty1` | decimal(19,8) | NO |
| 39 | `so_qty2` | decimal(19,8) | NO |
| 40 | `so_data_src` | varchar(1) | NO |
| 41 | `so_data_id` | varchar(255) | NO |
| 42 | `so_src` | varchar(2) | NO |
| 43 | `so_src_nbr` | varchar(15) | NO |
| 44 | `so_src_lot` | varchar(18) | NO |
| 45 | `so_allow` | bit | NO |
| 46 | `so_allow_by` | varchar(12) | NO |
| 47 | `so_allow_date` | datetime | YES |
| 48 | `so_po_chg` | bit | NO |
| 49 | `so_po_chg_by` | varchar(12) | NO |
| 50 | `so_po_chg_date` | datetime | YES |
| 51 | `so_po_chg_rmks` | varchar(255) | NO |
| 52 | `so_po_chk` | bit | NO |
| 53 | `so_po_chk_by` | varchar(12) | NO |
| 54 | `so_po_chk_date` | datetime | YES |

### `dbo.soc_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `soc_soc` | int(10,0) | NO |
| 2 | `soc_credit` | varchar(80) | NO |
| 3 | `soc_mod_price` | varchar(80) | NO |
| 4 | `soc_zero_price_sale` | varchar(80) | NO |
| 5 | `soc_all_cust` | varchar(80) | NO |
| 6 | `soc_cost_hint` | bit | NO |
| 7 | `soc_replace` | bit | NO |
| 8 | `soc_dna_req` | bit | NO |
| 9 | `soc_dna_autocls` | bit | NO |
| 10 | `soc_dn_other_part` | bit | NO |
| 11 | `soc_inv_alloc` | bit | NO |
| 12 | `soc_terms` | text(2147483647) | YES |
| 13 | `soc_char1` | varchar(255) | NO |
| 14 | `soc_char2` | varchar(255) | NO |
| 15 | `soc_char3` | varchar(255) | NO |
| 16 | `soc_char4` | varchar(255) | NO |
| 17 | `soc_char5` | varchar(255) | NO |
| 18 | `soc_char6` | varchar(255) | NO |
| 19 | `soc_qty1` | decimal(19,8) | NO |
| 20 | `soc_qty2` | decimal(19,8) | NO |
| 21 | `soc_min_price_perm` | varchar(80) | NO |
| 22 | `soc_use_as` | bit | NO |
| 23 | `soc_edit_spec_req` | varchar(80) | NO |
| 24 | `soc_pst_spec_req` | varchar(80) | NO |
| 25 | `soc_unpst_spec_req` | varchar(80) | NO |
| 26 | `soc_mod_price_af_ar` | varchar(80) | YES |

### `dbo.sod_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sod_nbr` | varchar(15) | NO |
| 2 | `sod_line` | int(10,0) | NO |
| 3 | `sod_part` | varchar(30) | NO |
| 4 | `sod_cust_part` | varchar(80) | NO |
| 5 | `sod_um` | varchar(4) | NO |
| 6 | `sod_um_rate_m` | decimal(19,8) | NO |
| 7 | `sod_um_rate_d` | decimal(19,8) | NO |
| 8 | `sod_qty_ord` | numeric(19,8) | NO |
| 9 | `sod_qty_spare` | numeric(19,8) | NO |
| 10 | `sod_qty_shp` | numeric(19,8) | NO |
| 11 | `sod_qty_rtn` | numeric(19,8) | NO |
| 12 | `sod_qty_spare_shp` | numeric(19,8) | NO |
| 13 | `sod_qty_spare_rtn` | numeric(19,8) | NO |
| 14 | `sod_list_price` | numeric(19,8) | NO |
| 15 | `sod_disc` | decimal(19,8) | NO |
| 16 | `sod_price` | decimal(19,8) | NO |
| 17 | `sod_req_date` | datetime | NO |
| 18 | `sod_due_date` | datetime | NO |
| 19 | `sod_promise_date` | datetime | YES |
| 20 | `sod_fix_pr` | bit | NO |
| 21 | `sod_qty_alloc` | numeric(19,8) | NO |
| 22 | `sod_rtn_flag` | bit | NO |
| 23 | `sod_cmmt` | varchar(255) | NO |
| 24 | `sod_status` | varchar(1) | NO |
| 25 | `sod_close_by` | varchar(12) | NO |
| 26 | `sod_close_date` | datetime | YES |
| 27 | `sod_ac_income` | varchar(15) | NO |
| 28 | `sod_crt_by` | varchar(12) | NO |
| 29 | `sod_crt_date` | datetime | NO |
| 30 | `sod_mod_times` | int(10,0) | NO |
| 31 | `sod_mod_by` | varchar(12) | NO |
| 32 | `sod_mod_date` | datetime | NO |
| 33 | `sod_char1` | varchar(255) | NO |
| 34 | `sod_char2` | varchar(255) | NO |
| 35 | `sod_char3` | varchar(255) | NO |
| 36 | `sod_char4` | varchar(255) | NO |
| 37 | `sod_char5` | varchar(255) | NO |
| 38 | `sod_char6` | varchar(255) | NO |
| 39 | `sod_qty1` | decimal(19,8) | NO |
| 40 | `sod_qty2` | decimal(19,8) | NO |
| 41 | `sod_ast_code` | varchar(15) | NO |
| 42 | `sod_req_pst` | bit | NO |
| 43 | `sod_req_pst_by` | varchar(12) | NO |
| 44 | `sod_req_pst_date` | datetime | YES |
| 45 | `sod_data_src` | varchar(1) | NO |
| 46 | `sod_data_id` | varchar(255) | NO |
| 47 | `sod_pt_desc` | varchar(255) | NO |
| 48 | `sod_pt_spec` | varchar(255) | NO |
| 49 | `sod_wo_req` | varchar(255) | NO |
| 50 | `sod_src` | varchar(2) | NO |
| 51 | `sod_src_nbr` | varchar(15) | NO |
| 52 | `sod_src_line` | int(10,0) | NO |
| 53 | `sod_cu_area` | varchar(30) | NO |
| 54 | `sod_cu_curr` | varchar(30) | NO |
| 55 | `sod_cu_price` | numeric(19,8) | NO |
| 56 | `sod_price_type` | varchar(1) | NO |
| 57 | `sod_close_reason` | varchar(255) | NO |

### `dbo.sodb_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sodb_nbr` | varchar(15) | NO |
| 2 | `sodb_line` | int(10,0) | NO |
| 3 | `sodb_seq` | int(10,0) | NO |
| 4 | `sodb_type` | varchar(1) | NO |
| 5 | `sodb_part_af` | varchar(30) | NO |
| 6 | `sodb_part_bf` | varchar(30) | NO |
| 7 | `sodb_qty_per_m` | numeric(19,8) | NO |
| 8 | `sodb_qty_per_d` | numeric(19,8) | NO |
| 9 | `sodb_rmks` | varchar(255) | NO |
| 10 | `sodb_crt_by` | varchar(12) | NO |
| 11 | `sodb_crt_date` | datetime | NO |
| 12 | `sodb_mod_times` | int(10,0) | NO |
| 13 | `sodb_mod_by` | varchar(12) | NO |
| 14 | `sodb_mod_date` | datetime | NO |
| 15 | `sodb_char1` | varchar(255) | NO |
| 16 | `sodb_char2` | varchar(255) | NO |
| 17 | `sodb_char3` | varchar(255) | NO |
| 18 | `sodb_char4` | varchar(255) | NO |
| 19 | `sodb_char5` | varchar(255) | NO |
| 20 | `sodb_char6` | varchar(255) | NO |
| 21 | `sodb_qty1` | decimal(19,8) | NO |
| 22 | `sodb_qty2` | decimal(19,8) | NO |

### `dbo.som_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `som_so_nbr` | varchar(15) | NO |
| 2 | `som_so_rev` | varchar(4) | NO |
| 3 | `som_bf_so_addr` | varchar(255) | NO |
| 4 | `som_bf_so_po` | varchar(255) | NO |
| 5 | `som_bf_so_cr_terms` | varchar(10) | NO |
| 6 | `som_bf_so_slspsn` | varchar(12) | NO |
| 7 | `som_bf_so_curr` | varchar(4) | NO |
| 8 | `som_bf_so_ex_rate` | decimal(19,8) | NO |
| 9 | `som_bf_so_vat` | decimal(19,8) | NO |
| 10 | `som_bf_so_rev` | varchar(4) | NO |
| 11 | `som_bf_so_rmks` | varchar(255) | NO |
| 12 | `som_bf_so_terms` | text(2147483647) | YES |
| 13 | `som_bf_so_char1` | varchar(255) | NO |
| 14 | `som_bf_so_char2` | varchar(255) | NO |
| 15 | `som_bf_so_char3` | varchar(255) | NO |
| 16 | `som_bf_so_char4` | varchar(255) | NO |
| 17 | `som_bf_so_char5` | varchar(255) | NO |
| 18 | `som_bf_so_char6` | varchar(255) | NO |
| 19 | `som_bf_so_qty1` | decimal(19,8) | NO |
| 20 | `som_bf_so_qty2` | decimal(19,8) | NO |
| 21 | `som_af_so_addr` | varchar(255) | NO |
| 22 | `som_af_so_po` | varchar(255) | NO |
| 23 | `som_af_so_cr_terms` | varchar(10) | NO |
| 24 | `som_af_so_slspsn` | varchar(12) | NO |
| 25 | `som_af_so_curr` | varchar(4) | NO |
| 26 | `som_af_so_ex_rate` | decimal(19,8) | NO |
| 27 | `som_af_so_vat` | decimal(19,8) | NO |
| 28 | `som_af_so_rmks` | varchar(255) | NO |
| 29 | `som_af_so_terms` | text(2147483647) | YES |
| 30 | `som_af_so_char1` | varchar(255) | NO |
| 31 | `som_af_so_char2` | varchar(255) | NO |
| 32 | `som_af_so_char3` | varchar(255) | NO |
| 33 | `som_af_so_char4` | varchar(255) | NO |
| 34 | `som_af_so_char5` | varchar(255) | NO |
| 35 | `som_af_so_char6` | varchar(255) | NO |
| 36 | `som_af_so_qty1` | decimal(19,8) | NO |
| 37 | `som_af_so_qty2` | decimal(19,8) | NO |
| 38 | `som_rmks` | varchar(255) | NO |
| 39 | `som_wf_status` | varchar(1) | NO |
| 40 | `som_site` | varchar(8) | NO |
| 41 | `som_prog_code` | varchar(12) | NO |
| 42 | `som_doc_code` | varchar(12) | NO |
| 43 | `som_crt_by` | varchar(12) | NO |
| 44 | `som_crt_date` | datetime | NO |
| 45 | `som_mod_times` | int(10,0) | NO |
| 46 | `som_mod_by` | varchar(12) | NO |
| 47 | `som_mod_date` | datetime | NO |
| 48 | `som_pst` | bit | NO |
| 49 | `som_pst_by` | varchar(12) | NO |
| 50 | `som_pst_date` | datetime | YES |
| 51 | `som_char1` | varchar(255) | NO |
| 52 | `som_char2` | varchar(255) | NO |
| 53 | `som_char3` | varchar(255) | NO |
| 54 | `som_char4` | varchar(255) | NO |
| 55 | `som_char5` | varchar(255) | NO |
| 56 | `som_char6` | varchar(255) | NO |
| 57 | `som_qty1` | decimal(19,8) | NO |
| 58 | `som_qty2` | decimal(19,8) | NO |

### `dbo.somd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `somd_so_nbr` | varchar(15) | NO |
| 2 | `somd_so_rev` | varchar(4) | NO |
| 3 | `somd_line` | int(10,0) | NO |
| 4 | `somd_type` | varchar(1) | NO |
| 5 | `somd_sod_line` | int(10,0) | NO |
| 6 | `somd_sod_part` | varchar(30) | NO |
| 7 | `somd_sod_cust_part` | varchar(80) | NO |
| 8 | `somd_sod_um` | varchar(4) | NO |
| 9 | `somd_bf_sod_qty_ord` | numeric(19,8) | NO |
| 10 | `somd_bf_sod_qty_spare` | numeric(19,8) | NO |
| 11 | `somd_bf_sod_list_price` | decimal(19,8) | NO |
| 12 | `somd_bf_sod_disc` | decimal(19,8) | NO |
| 13 | `somd_bf_sod_price` | decimal(19,8) | NO |
| 14 | `somd_bf_sod_req_date` | datetime | YES |
| 15 | `somd_bf_sod_due_date` | datetime | YES |
| 16 | `somd_bf_sod_um_rate_m` | decimal(19,8) | NO |
| 17 | `somd_bf_sod_um_rate_d` | decimal(19,8) | NO |
| 18 | `somd_bf_sod_char1` | varchar(30) | NO |
| 19 | `somd_bf_sod_char2` | varchar(30) | NO |
| 20 | `somd_bf_sod_char3` | varchar(30) | NO |
| 21 | `somd_bf_sod_char4` | varchar(30) | NO |
| 22 | `somd_bf_sod_char5` | varchar(30) | NO |
| 23 | `somd_bf_sod_char6` | varchar(30) | NO |
| 24 | `somd_bf_sod_qty1` | numeric(19,8) | NO |
| 25 | `somd_bf_sod_qty2` | numeric(19,8) | NO |
| 26 | `somd_af_sod_qty_ord` | numeric(19,8) | NO |
| 27 | `somd_af_sod_qty_spare` | numeric(19,8) | NO |
| 28 | `somd_af_sod_list_price` | decimal(19,8) | NO |
| 29 | `somd_af_sod_disc` | decimal(19,8) | NO |
| 30 | `somd_af_sod_price` | decimal(19,8) | NO |
| 31 | `somd_af_sod_req_date` | datetime | NO |
| 32 | `somd_af_sod_due_date` | datetime | NO |
| 33 | `somd_af_sod_um_rate_m` | decimal(19,8) | NO |
| 34 | `somd_af_sod_um_rate_d` | decimal(19,8) | NO |
| 35 | `somd_af_sod_char1` | varchar(30) | NO |
| 36 | `somd_af_sod_char2` | varchar(30) | NO |
| 37 | `somd_af_sod_char3` | varchar(30) | NO |
| 38 | `somd_af_sod_char4` | varchar(30) | NO |
| 39 | `somd_af_sod_char5` | varchar(30) | NO |
| 40 | `somd_af_sod_char6` | varchar(30) | NO |
| 41 | `somd_af_sod_qty1` | numeric(19,8) | NO |
| 42 | `somd_af_sod_qty2` | numeric(19,8) | NO |
| 43 | `somd_reason` | varchar(255) | NO |
| 44 | `somd_rmks` | varchar(255) | NO |
| 45 | `somd_crt_by` | varchar(12) | NO |
| 46 | `somd_crt_date` | datetime | NO |
| 47 | `somd_mod_times` | int(10,0) | NO |
| 48 | `somd_mod_by` | varchar(12) | NO |
| 49 | `somd_mod_date` | datetime | NO |
| 50 | `somd_char1` | varchar(255) | NO |
| 51 | `somd_char2` | varchar(255) | NO |
| 52 | `somd_char3` | varchar(255) | NO |
| 53 | `somd_char4` | varchar(255) | NO |
| 54 | `somd_char5` | varchar(255) | NO |
| 55 | `somd_char6` | varchar(255) | NO |
| 56 | `somd_qty1` | decimal(19,8) | NO |
| 57 | `somd_qty2` | decimal(19,8) | NO |
| 58 | `somd_bf_ast_code` | varchar(15) | NO |
| 59 | `somd_af_ast_code` | varchar(15) | NO |
| 60 | `somd_bf_sod_cust_part` | varchar(80) | NO |
| 61 | `somd_bf_sod_cmmt` | varchar(255) | YES |
| 62 | `somd_af_sod_cmmt` | varchar(255) | YES |
| 63 | `somd_bf_sod_cu_area` | varchar(30) | NO |
| 64 | `somd_bf_sod_cu_curr` | varchar(30) | NO |
| 65 | `somd_bf_sod_cu_price` | numeric(19,8) | NO |
| 66 | `somd_bf_sod_price_type` | varchar(1) | NO |
| 67 | `somd_af_sod_cu_area` | varchar(30) | NO |
| 68 | `somd_af_sod_cu_curr` | varchar(30) | NO |
| 69 | `somd_af_sod_cu_price` | numeric(19,8) | NO |
| 70 | `somd_af_sod_price_type` | varchar(1) | NO |

### `dbo.spr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `spr_id` | uniqueidentifier | NO |
| 2 | `spr_date` | datetime | YES |
| 3 | `spr_loc` | nvarchar(20) | YES |
| 4 | `spr_loc_pos` | nvarchar(20) | YES |
| 5 | `spr_part` | nvarchar(36) | YES |
| 6 | `spr_rmks` | nvarchar(255) | YES |
| 7 | `spr_prog_code` | nvarchar(20) | YES |
| 8 | `spr_crt_by` | nvarchar(40) | YES |
| 9 | `spr_crt_date` | datetime | YES |
| 10 | `spr_mod_times` | int(10,0) | YES |
| 11 | `spr_mod_by` | nvarchar(40) | YES |
| 12 | `spr_mod_date` | datetime | YES |
| 13 | `spr_pst` | tinyint(3,0) | YES |
| 14 | `spr_pst_by` | nvarchar(40) | YES |
| 15 | `spr_pst_date` | datetime | YES |
| 16 | `spr_char1` | nvarchar(255) | YES |
| 17 | `spr_char2` | nvarchar(255) | YES |
| 18 | `spr_char3` | nvarchar(255) | YES |
| 19 | `spr_char4` | nvarchar(255) | YES |
| 20 | `spr_char5` | nvarchar(255) | YES |
| 21 | `spr_char6` | nvarchar(255) | YES |
| 22 | `spr_qty1` | decimal(19,8) | YES |
| 23 | `spr_qty2` | decimal(19,8) | YES |

### `dbo.sys_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sys_sys` | int(10,0) | NO |
| 2 | `sys_name1` | varchar(50) | NO |
| 3 | `sys_name2` | varchar(50) | NO |
| 4 | `sys_dt_fmt` | varchar(30) | NO |
| 5 | `sys_lib_path` | varchar(255) | NO |
| 6 | `sys_min_date` | datetime | NO |
| 7 | `sys_max_date` | datetime | NO |
| 8 | `sys_start` | datetime | NO |
| 9 | `sys_min_price` | int(10,0) | NO |
| 10 | `sys_min_amt` | int(10,0) | NO |
| 11 | `sys_min_qty` | int(10,0) | NO |
| 12 | `sys_mult_site` | bit | NO |
| 13 | `sys_cost_type` | varchar(1) | NO |
| 14 | `sys_costing` | varchar(8) | NO |
| 15 | `sys_pst_flag` | bit | NO |
| 16 | `sys_version` | varchar(10) | NO |
| 17 | `sys_patch_version` | varchar(10) | NO |
| 18 | `sys_cal_day` | int(10,0) | NO |
| 19 | `sys_pt_ver_ctrl` | bit | NO |
| 20 | `sys_attach_db` | varchar(30) | NO |
| 21 | `sys_att_max_size` | int(10,0) | NO |
| 22 | `sys_inv_cyear` | int(10,0) | NO |
| 23 | `sys_inv_cmonth` | int(10,0) | NO |
| 24 | `sys_inv_lyear` | int(10,0) | NO |
| 25 | `sys_inv_lmonth` | int(10,0) | NO |
| 26 | `sys_f_cyear` | int(10,0) | NO |
| 27 | `sys_f_cmonth` | int(10,0) | NO |
| 28 | `sys_f_lyear` | int(10,0) | NO |
| 29 | `sys_f_lmonth` | int(10,0) | NO |
| 30 | `sys_ar_cyear` | int(10,0) | NO |
| 31 | `sys_ar_cmonth` | int(10,0) | NO |
| 32 | `sys_ar_lyear` | int(10,0) | NO |
| 33 | `sys_ar_lmonth` | int(10,0) | NO |
| 34 | `sys_ap_cyear` | int(10,0) | NO |
| 35 | `sys_ap_cmonth` | int(10,0) | NO |
| 36 | `sys_ap_lyear` | int(10,0) | NO |
| 37 | `sys_ap_lmonth` | int(10,0) | NO |
| 38 | `sys_crt_by` | varchar(12) | NO |
| 39 | `sys_crt_date` | datetime | NO |
| 40 | `sys_char1` | varchar(255) | NO |
| 41 | `sys_char2` | varchar(255) | NO |
| 42 | `sys_char3` | varchar(255) | NO |
| 43 | `sys_char4` | varchar(255) | NO |
| 44 | `sys_char5` | varchar(255) | NO |
| 45 | `sys_char6` | varchar(255) | NO |
| 46 | `sys_qty1` | decimal(19,8) | NO |
| 47 | `sys_qty2` | decimal(19,8) | NO |
| 48 | `sys_module_code` | varchar(255) | NO |
| 49 | `sys_incl_vat` | bit | NO |
| 50 | `sys_double_um` | bit | NO |
| 51 | `sys_cu_price` | bit | NO |
| 52 | `sys_spec_char` | bit | NO |
| 53 | `sys_dup_desc` | varchar(1) | NO |
| 54 | `sys_report_url` | varchar(255) | NO |
| 55 | `sys_report_prefix` | varchar(30) | NO |
| 56 | `sys_update_path` | varchar(255) | NO |
| 57 | `sys_inb_qty` | bit | NO |
| 58 | `sys_pass_min_len` | int(10,0) | NO |
| 59 | `sys_pass_comp` | varchar(1) | NO |
| 60 | `sys_pass_first` | bit | NO |
| 61 | `sys_pass_mod` | bit | NO |
| 62 | `sys_pass_days` | int(10,0) | NO |
| 63 | `sys_pass_warning` | int(10,0) | NO |
| 64 | `sys_last_month` | int(10,0) | NO |
| 65 | `sys_price_type` | varchar(1) | NO |
| 66 | `sys_sync_web` | bit | NO |
| 67 | `sys_sync_scm` | bit | NO |
| 68 | `sys_co_id` | varchar(30) | NO |
| 69 | `sys_dup` | varchar(1) | NO |
| 70 | `sys_auto_fill` | bit | NO |
| 71 | `sys_sync_dest` | varchar(255) | NO |

### `dbo.tpt_barcode` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `bc_user` | varchar(12) | NO |
| 2 | `bc_flow` | int(10,0) | NO |
| 3 | `bc_key1` | varchar(30) | NO |
| 4 | `bc_key2` | varchar(30) | NO |
| 5 | `bc_key3` | varchar(30) | NO |
| 6 | `bc_key4` | varchar(30) | NO |
| 7 | `bc_key5` | varchar(30) | NO |
| 8 | `bc_code` | varchar(2000) | NO |
| 9 | `bc_img` | image(2147483647) | YES |
| 10 | `bc_value1` | varchar(50) | NO |
| 11 | `bc_value2` | varchar(50) | NO |
| 12 | `bc_value3` | varchar(50) | NO |
| 13 | `bc_value4` | varchar(50) | NO |
| 14 | `bc_value5` | varchar(50) | NO |
| 15 | `bc_value6` | varchar(50) | NO |
| 16 | `bc_value7` | varchar(50) | NO |
| 17 | `bc_value8` | varchar(50) | NO |
| 18 | `bc_value9` | varchar(50) | NO |
| 19 | `bc_qty1` | numeric(19,8) | NO |
| 20 | `bc_qty2` | numeric(19,8) | NO |
| 21 | `bc_qty3` | numeric(19,8) | NO |
| 22 | `bc_qty4` | numeric(19,8) | NO |
| 23 | `bc_qty5` | numeric(19,8) | NO |
| 24 | `bc_qty6` | numeric(19,8) | NO |
| 25 | `bc_qty7` | numeric(19,8) | NO |
| 26 | `bc_qty8` | numeric(19,8) | NO |
| 27 | `bc_qty9` | numeric(19,8) | NO |
| 28 | `bc_date1` | datetime | YES |
| 29 | `bc_date2` | datetime | YES |
| 30 | `bc_date3` | datetime | YES |
| 31 | `bc_date4` | datetime | YES |
| 32 | `bc_text1` | varchar(50) | NO |
| 33 | `bc_text2` | varchar(50) | NO |
| 34 | `bc_text3` | varchar(50) | NO |
| 35 | `bc_text4` | varchar(50) | NO |

### `dbo.tpt_inb_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inb_year_fr` | int(10,0) | NO |
| 2 | `inb_month_fr` | int(10,0) | NO |
| 3 | `inb_year_to` | int(10,0) | NO |
| 4 | `inb_month_to` | int(10,0) | NO |
| 5 | `inb_site` | varchar(8) | NO |
| 6 | `inb_part` | varchar(30) | NO |
| 7 | `inb_loc` | varchar(8) | NO |
| 8 | `inb_lot` | varchar(18) | NO |
| 9 | `inb_qty_beg` | numeric(19,8) | NO |
| 10 | `inb_qty_end` | numeric(19,8) | NO |
| 11 | `inb_cost_beg` | numeric(19,8) | NO |
| 12 | `inb_cost_end` | numeric(19,8) | NO |
| 13 | `inb_char1` | varchar(255) | NO |
| 14 | `inb_char2` | varchar(255) | NO |
| 15 | `inb_char3` | varchar(255) | NO |
| 16 | `inb_char4` | varchar(255) | NO |
| 17 | `inb_char5` | varchar(255) | NO |
| 18 | `inb_char6` | varchar(255) | NO |
| 19 | `inb_qty1` | decimal(19,8) | NO |
| 20 | `inb_qty2` | decimal(19,8) | NO |

### `dbo.tpt_ptp3_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ptp3_year` | int(10,0) | NO |
| 2 | `ptp3_month` | int(10,0) | NO |
| 3 | `ptp3_site` | varchar(8) | NO |
| 4 | `ptp3_part` | varchar(30) | NO |
| 5 | `ptp3_mtl_stdtl` | decimal(19,8) | NO |
| 6 | `ptp3_mtl_stdll` | decimal(19,8) | NO |
| 7 | `ptp3_lbr_stdtl` | decimal(19,8) | NO |
| 8 | `ptp3_lbr_stdll` | decimal(19,8) | NO |
| 9 | `ptp3_bdn_stdtl` | decimal(19,8) | NO |
| 10 | `ptp3_bdn_stdll` | decimal(19,8) | NO |
| 11 | `ptp3_sub_stdtl` | decimal(19,8) | NO |
| 12 | `ptp3_sub_stdll` | decimal(19,8) | NO |
| 13 | `ptp3_char1` | varchar(255) | NO |
| 14 | `ptp3_char2` | varchar(255) | NO |
| 15 | `ptp3_char3` | varchar(255) | NO |
| 16 | `ptp3_char4` | varchar(255) | NO |
| 17 | `ptp3_char5` | varchar(255) | NO |
| 18 | `ptp3_char6` | varchar(255) | NO |
| 19 | `ptp3_qty1` | decimal(19,8) | NO |
| 20 | `ptp3_qty2` | decimal(19,8) | NO |

### `dbo.tpt_table` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_prog` | varchar(50) | NO |
| 2 | `tmp_char01` | varchar(255) | NO |
| 3 | `tmp_char02` | varchar(255) | NO |
| 4 | `tmp_char03` | varchar(255) | NO |
| 5 | `tmp_char04` | varchar(255) | NO |
| 6 | `tmp_char05` | varchar(255) | NO |
| 7 | `tmp_char06` | varchar(255) | NO |
| 8 | `tmp_char07` | varchar(255) | NO |
| 9 | `tmp_char08` | varchar(255) | NO |
| 10 | `tmp_char09` | varchar(255) | NO |
| 11 | `tmp_int01` | int(10,0) | NO |
| 12 | `tmp_int02` | int(10,0) | NO |
| 13 | `tmp_int03` | int(10,0) | NO |
| 14 | `tmp_int04` | int(10,0) | NO |
| 15 | `tmp_int05` | int(10,0) | NO |
| 16 | `tmp_int06` | int(10,0) | NO |
| 17 | `tmp_int07` | int(10,0) | NO |
| 18 | `tmp_int08` | int(10,0) | NO |
| 19 | `tmp_int09` | int(10,0) | NO |
| 20 | `tmp_qty01` | numeric(19,8) | NO |
| 21 | `tmp_qty02` | numeric(19,8) | NO |
| 22 | `tmp_qty03` | numeric(19,8) | NO |
| 23 | `tmp_qty04` | numeric(19,8) | NO |
| 24 | `tmp_qty05` | numeric(19,8) | NO |
| 25 | `tmp_qty06` | numeric(19,8) | NO |
| 26 | `tmp_qty07` | numeric(19,8) | NO |
| 27 | `tmp_qty08` | numeric(19,8) | NO |
| 28 | `tmp_qty09` | numeric(19,8) | NO |
| 29 | `tmp_qty10` | numeric(19,8) | NO |
| 30 | `tmp_qty11` | numeric(19,8) | NO |
| 31 | `tmp_qty12` | numeric(19,8) | NO |
| 32 | `tmp_qty13` | numeric(19,8) | NO |
| 33 | `tmp_qty14` | numeric(19,8) | NO |
| 34 | `tmp_qty15` | numeric(19,8) | NO |
| 35 | `tmp_date01` | date | YES |
| 36 | `tmp_date02` | date | YES |
| 37 | `tmp_date03` | date | YES |
| 38 | `tmp_date04` | date | YES |
| 39 | `tmp_text01` | varchar(2000) | NO |
| 40 | `tmp_text02` | varchar(2000) | NO |

### `dbo.tpt_vch_src` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_user` | varchar(12) | NO |
| 2 | `tmp_flow` | int(10,0) | NO |
| 3 | `tmp_selected` | bit | NO |
| 4 | `tmp_src` | varchar(30) | NO |
| 5 | `tmp_src_nbr` | varchar(15) | NO |
| 6 | `tmp_prog_code` | varchar(12) | NO |
| 7 | `tmp_date` | datetime | NO |
| 8 | `tmp_addr` | varchar(30) | NO |
| 9 | `tmp_sort` | varchar(50) | NO |
| 10 | `tmp_curr` | varchar(4) | NO |
| 11 | `tmp_credit_amt` | numeric(19,8) | NO |
| 12 | `tmp_credit_amt_base` | numeric(19,8) | NO |
| 13 | `tmp_debit_amt` | numeric(19,8) | NO |
| 14 | `tmp_debit_amt_base` | numeric(19,8) | NO |
| 15 | `tmp_rmks` | varchar(255) | NO |
| 16 | `tmp_vt_code` | varchar(15) | NO |
| 17 | `tmp_ac_flag` | int(10,0) | NO |
| 18 | `tmp_group` | varchar(255) | NO |

### `dbo.tpt_vchd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tpt_vchd_user` | varchar(12) | NO |
| 2 | `tpt_vchd_src_prog` | varchar(12) | NO |
| 3 | `tpt_vchd_src_nbr` | varchar(15) | NO |
| 4 | `tpt_vchd_company` | varchar(8) | NO |
| 5 | `tpt_vchd_nbr` | varchar(15) | NO |
| 6 | `tpt_vchd_line` | int(10,0) | NO |
| 7 | `tpt_vchd_ac_code` | varchar(15) | NO |
| 8 | `tpt_vchd_content` | varchar(255) | NO |
| 9 | `tpt_vchd_curr` | varchar(4) | NO |
| 10 | `tpt_vchd_ex_rate` | decimal(19,8) | NO |
| 11 | `tpt_vchd_price` | decimal(19,8) | NO |
| 12 | `tpt_vchd_debit_amt` | numeric(19,8) | NO |
| 13 | `tpt_vchd_debit_base` | numeric(19,8) | NO |
| 14 | `tpt_vchd_debit_qty` | numeric(19,8) | NO |
| 15 | `tpt_vchd_credit_amt` | numeric(19,8) | NO |
| 16 | `tpt_vchd_credit_base` | numeric(19,8) | NO |
| 17 | `tpt_vchd_credit_qty` | numeric(19,8) | NO |
| 18 | `tpt_vchd_dept` | varchar(10) | NO |
| 19 | `tpt_vchd_vt_code1` | varchar(30) | NO |
| 20 | `tpt_vchd_vt_name1` | varchar(255) | NO |
| 21 | `tpt_vchd_vt_code2` | varchar(30) | NO |
| 22 | `tpt_vchd_vt_name2` | varchar(255) | NO |
| 23 | `tpt_vchd_vt_code3` | varchar(30) | NO |
| 24 | `tpt_vchd_vt_name3` | varchar(255) | NO |
| 25 | `tpt_vchd_vt_code4` | varchar(30) | NO |
| 26 | `tpt_vchd_vt_name4` | varchar(255) | NO |
| 27 | `tpt_vchd_due` | bit | NO |
| 28 | `tpt_vchd_checked` | bit | NO |
| 29 | `tpt_vchd_autochk` | bit | NO |
| 30 | `tpt_vchd_settle` | varchar(30) | NO |
| 31 | `tpt_vchd_settle_no` | varchar(50) | NO |
| 32 | `tpt_vchd_settle_date` | datetime | YES |
| 33 | `tpt_vchd_cash_item` | varchar(30) | NO |
| 34 | `tpt_vchd_rmks` | varchar(255) | NO |
| 35 | `tpt_vchd_crt_by` | varchar(12) | NO |
| 36 | `tpt_vchd_crt_date` | datetime | NO |
| 37 | `tpt_vchd_mod_times` | int(10,0) | NO |
| 38 | `tpt_vchd_mod_by` | varchar(12) | NO |
| 39 | `tpt_vchd_mod_date` | datetime | NO |
| 40 | `tpt_vchd_char1` | varchar(255) | NO |
| 41 | `tpt_vchd_char2` | varchar(255) | NO |
| 42 | `tpt_vchd_char3` | varchar(255) | NO |
| 43 | `tpt_vchd_char4` | varchar(255) | NO |
| 44 | `tpt_vchd_char5` | varchar(255) | NO |
| 45 | `tpt_vchd_char6` | varchar(255) | NO |
| 46 | `tpt_vchd_qty1` | numeric(19,8) | NO |
| 47 | `tpt_vchd_qty2` | numeric(19,8) | NO |

### `dbo.tpt_vchd_ex` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_user` | varchar(12) | NO |
| 2 | `tmp_selected` | bit | NO |
| 3 | `tmp_ac_code` | varchar(15) | NO |
| 4 | `tmp_curr` | varchar(4) | NO |
| 5 | `tmp_d_c` | varchar(1) | NO |
| 6 | `tmp_amt` | numeric(19,8) | NO |
| 7 | `tmp_amt_base` | numeric(19,8) | NO |
| 8 | `tmp_ex_rate_org` | numeric(19,8) | NO |
| 9 | `tmp_ex_rate` | decimal(19,8) | NO |
| 10 | `tmp_amt_adj` | numeric(19,8) | NO |
| 11 | `tmp_char1` | varchar(255) | NO |
| 12 | `tmp_char2` | varchar(255) | NO |
| 13 | `tmp_char3` | varchar(255) | NO |
| 14 | `tmp_char4` | varchar(255) | NO |
| 15 | `tmp_char5` | varchar(255) | NO |
| 16 | `tmp_char6` | varchar(255) | NO |
| 17 | `tmp_qty1` | decimal(19,8) | NO |
| 18 | `tmp_qty2` | decimal(19,8) | NO |

### `dbo.tpt_vchd2_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tpt_vchd2_user` | varchar(12) | NO |
| 2 | `tpt_vchd2_src_prog` | varchar(12) | NO |
| 3 | `tpt_vchd2_src_nbr` | varchar(15) | NO |
| 4 | `tpt_vchd2_nbr` | varchar(15) | NO |
| 5 | `tpt_vchd2_line` | int(10,0) | NO |
| 6 | `tpt_vchd2_seq` | varchar(1) | NO |
| 7 | `tpt_vchd2_code` | varchar(30) | NO |
| 8 | `tpt_vchd2_debit_base` | numeric(19,8) | NO |
| 9 | `tpt_vchd2_credit_base` | numeric(19,8) | NO |
| 10 | `tpt_vchd2_crt_by` | varchar(12) | NO |
| 11 | `tpt_vchd2_crt_date` | datetime | NO |
| 12 | `tpt_vchd2_char1` | varchar(255) | NO |
| 13 | `tpt_vchd2_char2` | varchar(255) | NO |
| 14 | `tpt_vchd2_char3` | varchar(255) | NO |
| 15 | `tpt_vchd2_char4` | varchar(255) | NO |
| 16 | `tpt_vchd2_char5` | varchar(255) | NO |
| 17 | `tpt_vchd2_char6` | varchar(255) | NO |
| 18 | `tpt_vchd2_qty1` | decimal(19,8) | NO |
| 19 | `tpt_vchd2_qty2` | decimal(19,8) | NO |

### `dbo.tpt_vchd2_ex` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tmp_user` | varchar(12) | NO |
| 2 | `tmp_ac_code` | varchar(15) | NO |
| 3 | `tmp_curr` | varchar(4) | NO |
| 4 | `tmp_seq` | varchar(1) | NO |
| 5 | `tmp_code` | varchar(30) | NO |
| 6 | `tmp_d_c` | varchar(1) | NO |
| 7 | `tmp_amt` | numeric(19,8) | NO |
| 8 | `tmp_amt_base` | numeric(19,8) | NO |
| 9 | `tmp_ex_rate_org` | numeric(19,8) | NO |
| 10 | `tmp_ex_rate` | decimal(19,8) | NO |
| 11 | `tmp_amt_adj` | numeric(19,8) | NO |
| 12 | `tmp_char1` | varchar(255) | NO |
| 13 | `tmp_char2` | varchar(255) | NO |
| 14 | `tmp_char3` | varchar(255) | NO |
| 15 | `tmp_char4` | varchar(255) | NO |
| 16 | `tmp_char5` | varchar(255) | NO |
| 17 | `tmp_char6` | varchar(255) | NO |
| 18 | `tmp_qty1` | decimal(19,8) | NO |
| 19 | `tmp_qty2` | decimal(19,8) | NO |

### `dbo.tr_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tr_trnbr` | int(10,0) | NO |
| 2 | `tr_part` | varchar(30) | NO |
| 3 | `tr_type` | varchar(8) | NO |
| 4 | `tr_date` | datetime | NO |
| 5 | `tr_effdate` | datetime | NO |
| 6 | `tr_site` | varchar(8) | NO |
| 7 | `tr_loc` | varchar(8) | NO |
| 8 | `tr_qty_loc` | numeric(19,8) | NO |
| 9 | `tr_um` | varchar(4) | NO |
| 10 | `tr_um_rate_m` | decimal(19,8) | NO |
| 11 | `tr_um_rate_d` | decimal(19,8) | NO |
| 12 | `tr_um_stk` | varchar(4) | NO |
| 13 | `tr_nbr` | varchar(15) | NO |
| 14 | `tr_line` | int(10,0) | NO |
| 15 | `tr_price` | decimal(19,8) | NO |
| 16 | `tr_curr` | varchar(4) | NO |
| 17 | `tr_ex_rate` | decimal(19,8) | NO |
| 18 | `tr_so_job` | varchar(15) | NO |
| 19 | `tr_lot` | varchar(18) | NO |
| 20 | `tr_ref` | varchar(15) | NO |
| 21 | `tr_ref_line` | int(10,0) | NO |
| 22 | `tr_addr` | varchar(8) | NO |
| 23 | `tr_lotserial` | varchar(18) | NO |
| 24 | `tr_ord_rev` | varchar(4) | NO |
| 25 | `tr_grade` | varchar(2) | NO |
| 26 | `tr_rmks` | varchar(255) | NO |
| 27 | `tr_userid` | varchar(12) | NO |
| 28 | `tr_mtl_tl` | decimal(19,8) | NO |
| 29 | `tr_mtl_ll` | decimal(19,8) | NO |
| 30 | `tr_lbr_tl` | decimal(19,8) | NO |
| 31 | `tr_lbr_ll` | decimal(19,8) | NO |
| 32 | `tr_bdn_tl` | decimal(19,8) | NO |
| 33 | `tr_bdn_ll` | decimal(19,8) | NO |
| 34 | `tr_sub_tl` | decimal(19,8) | NO |
| 35 | `tr_sub_ll` | decimal(19,8) | NO |
| 36 | `tr_mtl_amt` | decimal(19,8) | NO |
| 37 | `tr_lbr_amt` | decimal(19,8) | NO |
| 38 | `tr_bdn_amt` | decimal(19,8) | NO |
| 39 | `tr_sub_amt` | decimal(19,8) | NO |
| 40 | `tr_mtl_amt_ll` | decimal(19,8) | NO |
| 41 | `tr_lbr_amt_ll` | decimal(19,8) | NO |
| 42 | `tr_bdn_amt_ll` | decimal(19,8) | NO |
| 43 | `tr_sub_amt_ll` | decimal(19,8) | NO |
| 44 | `tr_cost_flag` | bit | NO |
| 45 | `tr_char1` | varchar(255) | NO |
| 46 | `tr_char2` | varchar(255) | NO |
| 47 | `tr_char3` | varchar(255) | NO |
| 48 | `tr_char4` | varchar(255) | NO |
| 49 | `tr_char5` | varchar(255) | NO |
| 50 | `tr_char6` | varchar(255) | NO |
| 51 | `tr_qty1` | decimal(19,8) | NO |
| 52 | `tr_qty2` | decimal(19,8) | NO |

### `dbo.tr_hist_rec` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tr_trnbr` | int(10,0) | NO |
| 2 | `tr_part` | varchar(30) | NO |
| 3 | `tr_type` | varchar(8) | NO |
| 4 | `tr_date` | datetime | NO |
| 5 | `tr_effdate` | datetime | NO |
| 6 | `tr_site` | varchar(8) | NO |
| 7 | `tr_loc` | varchar(8) | NO |
| 8 | `tr_qty_loc` | numeric(19,8) | NO |
| 9 | `tr_um` | varchar(4) | NO |
| 10 | `tr_um_rate_m` | decimal(19,8) | NO |
| 11 | `tr_um_rate_d` | decimal(19,8) | NO |
| 12 | `tr_um_stk` | varchar(4) | NO |
| 13 | `tr_nbr` | varchar(15) | NO |
| 14 | `tr_line` | int(10,0) | NO |
| 15 | `tr_price` | decimal(19,8) | NO |
| 16 | `tr_curr` | varchar(4) | NO |
| 17 | `tr_ex_rate` | decimal(19,8) | NO |
| 18 | `tr_so_job` | varchar(15) | NO |
| 19 | `tr_lot` | varchar(18) | NO |
| 20 | `tr_ref` | varchar(15) | NO |
| 21 | `tr_ref_line` | int(10,0) | NO |
| 22 | `tr_addr` | varchar(8) | NO |
| 23 | `tr_lotserial` | varchar(18) | NO |
| 24 | `tr_ord_rev` | varchar(4) | NO |
| 25 | `tr_grade` | varchar(2) | NO |
| 26 | `tr_rmks` | varchar(255) | NO |
| 27 | `tr_userid` | varchar(12) | NO |
| 28 | `tr_mtl_tl` | decimal(19,8) | NO |
| 29 | `tr_mtl_ll` | decimal(19,8) | NO |
| 30 | `tr_lbr_tl` | decimal(19,8) | NO |
| 31 | `tr_lbr_ll` | decimal(19,8) | NO |
| 32 | `tr_bdn_tl` | decimal(19,8) | NO |
| 33 | `tr_bdn_ll` | decimal(19,8) | NO |
| 34 | `tr_sub_tl` | decimal(19,8) | NO |
| 35 | `tr_sub_ll` | decimal(19,8) | NO |
| 36 | `tr_mtl_amt` | decimal(19,8) | NO |
| 37 | `tr_lbr_amt` | decimal(19,8) | NO |
| 38 | `tr_bdn_amt` | decimal(19,8) | NO |
| 39 | `tr_sub_amt` | decimal(19,8) | NO |
| 40 | `tr_mtl_amt_ll` | decimal(19,8) | NO |
| 41 | `tr_lbr_amt_ll` | decimal(19,8) | NO |
| 42 | `tr_bdn_amt_ll` | decimal(19,8) | NO |
| 43 | `tr_sub_amt_ll` | decimal(19,8) | NO |
| 44 | `tr_cost_flag` | bit | NO |
| 45 | `tr_char1` | varchar(255) | NO |
| 46 | `tr_char2` | varchar(255) | NO |
| 47 | `tr_char3` | varchar(255) | NO |
| 48 | `tr_char4` | varchar(255) | NO |
| 49 | `tr_char5` | varchar(255) | NO |
| 50 | `tr_char6` | varchar(255) | NO |
| 51 | `tr_qty1` | decimal(19,8) | NO |
| 52 | `tr_qty2` | decimal(19,8) | NO |

### `dbo.trp_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `trp_flow` | int(10,0) | NO |
| 2 | `trp_effdate` | datetime | NO |
| 3 | `trp_date` | datetime | NO |
| 4 | `trp_tr_type` | varchar(8) | NO |
| 5 | `trp_type` | varchar(1) | NO |
| 6 | `trp_site` | varchar(8) | NO |
| 7 | `trp_loc` | varchar(8) | NO |
| 8 | `trp_pos` | varchar(30) | NO |
| 9 | `trp_part` | varchar(30) | NO |
| 10 | `trp_lot` | varchar(18) | NO |
| 11 | `trp_qty` | numeric(19,8) | NO |
| 12 | `trp_src_nbr` | varchar(15) | NO |
| 13 | `trp_src_line` | int(10,0) | NO |
| 14 | `trp_ref` | varchar(15) | NO |
| 15 | `trp_ref_line` | varchar(15) | NO |
| 16 | `trp_user` | varchar(12) | NO |
| 17 | `trp_char1` | varchar(255) | NO |
| 18 | `trp_char2` | varchar(255) | NO |
| 19 | `trp_char3` | varchar(255) | NO |
| 20 | `trp_char4` | varchar(255) | NO |
| 21 | `trp_char5` | varchar(255) | NO |
| 22 | `trp_char6` | varchar(255) | NO |
| 23 | `trp_qty1` | decimal(19,8) | NO |
| 24 | `trp_qty2` | decimal(19,8) | NO |

### `dbo.tsf_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tsf_tsf` | varchar(15) | NO |
| 2 | `tsf_date` | datetime | NO |
| 3 | `tsf_wo_line_fr` | varchar(8) | NO |
| 4 | `tsf_wo_line_to` | varchar(8) | NO |
| 5 | `tsf_rmks` | varchar(255) | NO |
| 6 | `tsf_crt_by` | varchar(12) | NO |
| 7 | `tsf_crt_date` | datetime | NO |
| 8 | `tsf_mod_times` | int(10,0) | NO |
| 9 | `tsf_mod_by` | varchar(12) | NO |
| 10 | `tsf_mod_date` | datetime | NO |
| 11 | `tsf_pst` | bit | NO |
| 12 | `tsf_pst_by` | varchar(12) | NO |
| 13 | `tsf_pst_date` | datetime | YES |
| 14 | `tsf_site` | varchar(8) | NO |
| 15 | `tsf_wf_status` | varchar(1) | NO |
| 16 | `tsf_prog_code` | varchar(12) | NO |
| 17 | `tsf_doc_code` | varchar(12) | NO |
| 18 | `tsf_char1` | varchar(255) | NO |
| 19 | `tsf_char2` | varchar(255) | NO |
| 20 | `tsf_char3` | varchar(255) | NO |
| 21 | `tsf_char4` | varchar(255) | NO |
| 22 | `tsf_char5` | varchar(255) | NO |
| 23 | `tsf_char6` | varchar(255) | NO |
| 24 | `tsf_qty1` | decimal(19,8) | NO |
| 25 | `tsf_qty2` | decimal(19,8) | NO |

### `dbo.tsfd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tsfd_tsf` | varchar(15) | NO |
| 2 | `tsfd_line` | int(10,0) | NO |
| 3 | `tsfd_wo_nbr_rtn` | varchar(15) | NO |
| 4 | `tsfd_wo_lot_rtn` | varchar(18) | NO |
| 5 | `tsfd_wo_line_fr` | varchar(8) | NO |
| 6 | `tsfd_part` | varchar(30) | NO |
| 7 | `tsfd_wo_nbr_iss` | varchar(15) | NO |
| 8 | `tsfd_wo_lot_iss` | varchar(18) | NO |
| 9 | `tsfd_wo_line_to` | varchar(8) | NO |
| 10 | `tsfd_wo_seq_iss` | int(10,0) | NO |
| 11 | `tsfd_loc` | varchar(8) | NO |
| 12 | `tsfd_qty` | numeric(19,8) | NO |
| 13 | `tsfd_lot` | varchar(18) | NO |
| 14 | `tsfd_rmks` | varchar(255) | NO |
| 15 | `tsfd_crt_by` | varchar(12) | NO |
| 16 | `tsfd_crt_date` | datetime | NO |
| 17 | `tsfd_mod_times` | int(10,0) | NO |
| 18 | `tsfd_mod_by` | varchar(12) | NO |
| 19 | `tsfd_mod_date` | datetime | NO |
| 20 | `tsfd_char1` | varchar(255) | NO |
| 21 | `tsfd_char2` | varchar(255) | NO |
| 22 | `tsfd_char3` | varchar(255) | NO |
| 23 | `tsfd_char4` | varchar(255) | NO |
| 24 | `tsfd_char5` | varchar(255) | NO |
| 25 | `tsfd_char6` | varchar(255) | NO |
| 26 | `tsfd_qty1` | decimal(19,8) | NO |
| 27 | `tsfd_qty2` | decimal(19,8) | NO |

### `dbo.udf_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `udf_table` | varchar(30) | NO |
| 2 | `udf_field` | varchar(30) | NO |
| 3 | `udf_prog` | varchar(30) | NO |
| 4 | `udf_lang` | varchar(3) | NO |
| 5 | `udf_visible` | bit | NO |
| 6 | `udf_readonly` | bit | NO |
| 7 | `udf_required` | bit | NO |
| 8 | `udf_default` | varchar(255) | NO |
| 9 | `udf_case` | varchar(30) | NO |
| 10 | `udf_caption` | varchar(30) | NO |
| 11 | `udf_hq` | varchar(30) | NO |
| 12 | `udf_valid` | varchar(255) | NO |
| 13 | `udf_msg` | varchar(255) | NO |
| 14 | `udf_crt_by` | varchar(12) | NO |
| 15 | `udf_crt_date` | datetime | NO |
| 16 | `udf_mod_times` | int(10,0) | NO |
| 17 | `udf_mod_by` | varchar(12) | NO |
| 18 | `udf_mod_date` | datetime | NO |
| 19 | `udf_char1` | varchar(255) | NO |
| 20 | `udf_char2` | varchar(255) | NO |
| 21 | `udf_char3` | varchar(255) | NO |
| 22 | `udf_char4` | varchar(255) | NO |
| 23 | `udf_char5` | varchar(255) | NO |
| 24 | `udf_char6` | varchar(255) | NO |
| 25 | `udf_qty1` | decimal(19,8) | NO |
| 26 | `udf_qty2` | decimal(19,8) | NO |
| 27 | `udf_amt` | bit | NO |

### `dbo.udqd1_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `udqd1_id` | varchar(15) | NO |
| 2 | `udqd1_field` | varchar(30) | NO |
| 3 | `udqd1_title` | varchar(30) | NO |
| 4 | `udqd1_idx` | int(10,0) | NO |
| 5 | `udqd1_amt` | bit | NO |
| 6 | `udqd1_align` | varchar(10) | NO |
| 7 | `udqd1_format` | varchar(30) | NO |
| 8 | `udqd1_summary` | varchar(10) | NO |
| 9 | `udqd1_show_zero` | bit | NO |
| 10 | `udqd1_link_prog` | varchar(255) | NO |
| 11 | `udqd1_link_doc` | varchar(12) | NO |
| 12 | `udqd1_link_lot` | varchar(30) | NO |
| 13 | `udqd1_crt_by` | varchar(12) | NO |
| 14 | `udqd1_crt_date` | datetime | NO |
| 15 | `udqd1_mod_times` | int(10,0) | NO |
| 16 | `udqd1_mod_by` | varchar(12) | NO |
| 17 | `udqd1_mod_date` | datetime | NO |
| 18 | `udqd1_char1` | varchar(255) | NO |
| 19 | `udqd1_char2` | varchar(255) | NO |
| 20 | `udqd1_char3` | varchar(255) | NO |
| 21 | `udqd1_char4` | varchar(255) | NO |
| 22 | `udqd1_char5` | varchar(255) | NO |
| 23 | `udqd1_char6` | varchar(255) | NO |
| 24 | `udqd1_qty1` | decimal(19,8) | NO |
| 25 | `udqd1_qty2` | decimal(19,8) | NO |
| 26 | `udqd1_fix` | bit | NO |
| 27 | `udqd1_prog_code` | bit | NO |
| 28 | `udqd1_link` | bit | NO |
| 29 | `udqd1_font_color` | bit | NO |
| 30 | `udqd1_sorting` | bit | NO |
| 31 | `udqd1_hide` | bit | NO |

### `dbo.um_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `um_um` | varchar(4) | NO |
| 2 | `um_desc` | varchar(30) | NO |
| 3 | `um_crt_by` | varchar(12) | NO |
| 4 | `um_crt_date` | datetime | NO |
| 5 | `um_char1` | varchar(255) | NO |
| 6 | `um_char2` | varchar(255) | NO |
| 7 | `um_char3` | varchar(255) | NO |
| 8 | `um_char4` | varchar(255) | NO |
| 9 | `um_char5` | varchar(255) | NO |
| 10 | `um_char6` | varchar(255) | NO |
| 11 | `um_qty1` | decimal(19,8) | NO |
| 12 | `um_qty2` | decimal(19,8) | NO |
| 13 | `um_ord_mult` | numeric(19,8) | NO |
| 14 | `um_iss_batch` | numeric(19,8) | YES |

### `dbo.usr_20250612` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `usr_user` | varchar(12) | NO |
| 2 | `usr_name` | varchar(30) | NO |
| 3 | `usr_group` | varchar(12) | NO |
| 4 | `usr_dept` | varchar(10) | NO |
| 5 | `usr_password` | varchar(50) | NO |
| 6 | `usr_lib_path` | varchar(80) | NO |
| 7 | `usr_def_site` | varchar(8) | NO |
| 8 | `usr_warning_circle` | int(10,0) | NO |
| 9 | `usr_employee` | bit | NO |
| 10 | `usr_lock` | bit | NO |
| 11 | `usr_out` | bit | NO |
| 12 | `usr_agent` | varchar(12) | NO |
| 13 | `usr_allow_ip` | varchar(255) | NO |
| 14 | `usr_crt_by` | varchar(12) | NO |
| 15 | `usr_crt_date` | datetime | NO |
| 16 | `usr_char1` | varchar(255) | NO |
| 17 | `usr_char2` | varchar(255) | NO |
| 18 | `usr_char3` | varchar(255) | NO |
| 19 | `usr_char4` | varchar(255) | NO |
| 20 | `usr_char5` | varchar(255) | NO |
| 21 | `usr_char6` | varchar(255) | NO |
| 22 | `usr_qty1` | decimal(19,8) | NO |
| 23 | `usr_qty2` | decimal(19,8) | NO |
| 24 | `usr_tele` | varchar(50) | NO |
| 25 | `usr_mobile` | varchar(50) | NO |
| 26 | `usr_email` | varchar(50) | NO |
| 27 | `usr_qq` | varchar(30) | NO |
| 28 | `usr_wechat` | varchar(50) | NO |
| 29 | `usr_other` | varchar(50) | NO |
| 30 | `usr_pos` | varchar(30) | NO |
| 31 | `usr_prog_cnt` | int(10,0) | NO |
| 32 | `usr_time_lmt` | int(10,0) | NO |
| 33 | `usr_lang` | varchar(10) | NO |
| 34 | `usr_type` | varchar(30) | NO |
| 35 | `usr_company` | varchar(255) | NO |
| 36 | `usr_cm_vd` | varchar(8) | NO |
| 37 | `usr_wx_id` | varchar(255) | NO |
| 38 | `usr_province` | varchar(30) | NO |
| 39 | `usr_city` | varchar(30) | NO |
| 40 | `usr_district` | varchar(30) | NO |
| 41 | `usr_address` | varchar(255) | NO |
| 42 | `usr_intro_by` | varchar(30) | NO |
| 43 | `usr_intro_mobile` | varchar(30) | NO |
| 44 | `usr_mod_times` | int(10,0) | NO |
| 45 | `usr_mod_by` | varchar(12) | NO |
| 46 | `usr_mod_date` | datetime | NO |
| 47 | `usr_pass_mod_date` | datetime | YES |
| 48 | `usr_wo_line` | varchar(8) | NO |
| 49 | `usr_device_id` | varchar(255) | NO |
| 50 | `usr_seq` | int(10,0) | NO |

### `dbo.usr_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `usr_user` | varchar(12) | NO |
| 2 | `usr_name` | varchar(30) | NO |
| 3 | `usr_group` | varchar(12) | NO |
| 4 | `usr_dept` | varchar(10) | NO |
| 5 | `usr_password` | varchar(50) | NO |
| 6 | `usr_lib_path` | varchar(80) | NO |
| 7 | `usr_def_site` | varchar(8) | NO |
| 8 | `usr_warning_circle` | int(10,0) | NO |
| 9 | `usr_employee` | bit | NO |
| 10 | `usr_lock` | bit | NO |
| 11 | `usr_out` | bit | NO |
| 12 | `usr_agent` | varchar(12) | NO |
| 13 | `usr_allow_ip` | varchar(255) | NO |
| 14 | `usr_crt_by` | varchar(12) | NO |
| 15 | `usr_crt_date` | datetime | NO |
| 16 | `usr_char1` | varchar(255) | NO |
| 17 | `usr_char2` | varchar(255) | NO |
| 18 | `usr_char3` | varchar(255) | NO |
| 19 | `usr_char4` | varchar(255) | NO |
| 20 | `usr_char5` | varchar(255) | NO |
| 21 | `usr_char6` | varchar(255) | NO |
| 22 | `usr_qty1` | decimal(19,8) | NO |
| 23 | `usr_qty2` | decimal(19,8) | NO |
| 24 | `usr_tele` | varchar(50) | NO |
| 25 | `usr_mobile` | varchar(50) | NO |
| 26 | `usr_email` | varchar(50) | NO |
| 27 | `usr_qq` | varchar(30) | NO |
| 28 | `usr_wechat` | varchar(50) | NO |
| 29 | `usr_other` | varchar(50) | NO |
| 30 | `usr_pos` | varchar(30) | NO |
| 31 | `usr_prog_cnt` | int(10,0) | NO |
| 32 | `usr_time_lmt` | int(10,0) | NO |
| 33 | `usr_lang` | varchar(10) | NO |
| 34 | `usr_type` | varchar(30) | NO |
| 35 | `usr_company` | varchar(255) | NO |
| 36 | `usr_cm_vd` | varchar(8) | NO |
| 37 | `usr_wx_id` | varchar(255) | NO |
| 38 | `usr_province` | varchar(30) | NO |
| 39 | `usr_city` | varchar(30) | NO |
| 40 | `usr_district` | varchar(30) | NO |
| 41 | `usr_address` | varchar(255) | NO |
| 42 | `usr_intro_by` | varchar(30) | NO |
| 43 | `usr_intro_mobile` | varchar(30) | NO |
| 44 | `usr_mod_times` | int(10,0) | NO |
| 45 | `usr_mod_by` | varchar(12) | NO |
| 46 | `usr_mod_date` | datetime | NO |
| 47 | `usr_pass_mod_date` | datetime | YES |
| 48 | `usr_wo_line` | varchar(8) | NO |
| 49 | `usr_device_id` | varchar(255) | NO |
| 50 | `usr_seq` | int(10,0) | NO |

### `dbo.usrp_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `usrp_user` | varchar(12) | NO |
| 2 | `usrp_prog` | varchar(12) | NO |
| 3 | `usrp_run` | bit | NO |
| 4 | `usrp_insert` | bit | NO |
| 5 | `usrp_modify` | bit | NO |
| 6 | `usrp_delete` | bit | NO |
| 7 | `usrp_print` | bit | NO |
| 8 | `usrp_export` | bit | NO |
| 9 | `usrp_pst` | bit | NO |
| 10 | `usrp_unpst` | bit | NO |
| 11 | `usrp_chk` | bit | NO |
| 12 | `usrp_unchk` | bit | NO |
| 13 | `usrp_wf_submit` | bit | NO |
| 14 | `usrp_wf_cancel` | bit | NO |
| 15 | `usrp_view_cost` | bit | NO |
| 16 | `usrp_view_others` | bit | NO |
| 17 | `usrp_mod_others` | bit | NO |
| 18 | `usrp_del_others` | bit | NO |
| 19 | `usrp_design` | bit | NO |
| 20 | `usrp_negative` | bit | NO |
| 21 | `usrp_perm1` | bit | NO |
| 22 | `usrp_perm2` | bit | NO |
| 23 | `usrp_perm3` | bit | NO |
| 24 | `usrp_perm4` | bit | NO |
| 25 | `usrp_perm5` | bit | NO |
| 26 | `usrp_perm6` | bit | NO |
| 27 | `usrp_char1` | varchar(255) | NO |
| 28 | `usrp_char2` | varchar(255) | NO |
| 29 | `usrp_char3` | varchar(255) | NO |
| 30 | `usrp_char4` | varchar(255) | NO |
| 31 | `usrp_char5` | varchar(255) | NO |
| 32 | `usrp_char6` | varchar(255) | NO |
| 33 | `usrp_qty1` | decimal(19,8) | NO |
| 34 | `usrp_qty2` | decimal(19,8) | NO |
| 35 | `usrp_invld` | bit | NO |
| 36 | `usrp_uninvld` | bit | NO |
| 37 | `usrp_att_insert` | bit | NO |
| 38 | `usrp_att_view` | bit | NO |
| 39 | `usrp_att_view_oth` | bit | NO |
| 40 | `usrp_att_download` | bit | NO |
| 41 | `usrp_att_down_oth` | bit | NO |
| 42 | `usrp_att_del` | bit | NO |
| 43 | `usrp_att_del_oth` | bit | NO |
| 44 | `usrp_perm7` | bit | NO |
| 45 | `usrp_perm8` | bit | NO |
| 46 | `usrp_perm9` | bit | NO |
| 47 | `usrp_rmks1` | varchar(255) | NO |
| 48 | `usrp_rmks2` | varchar(255) | NO |
| 49 | `usrp_rmks3` | varchar(255) | NO |
| 50 | `usrp_rmks4` | varchar(255) | NO |
| 51 | `usrp_rmks5` | varchar(255) | NO |
| 52 | `usrp_rmks6` | varchar(255) | NO |
| 53 | `usrp_rmks7` | varchar(255) | NO |
| 54 | `usrp_rmks8` | varchar(255) | NO |
| 55 | `usrp_rmks9` | varchar(255) | NO |
| 56 | `usrp_rmks` | varchar(255) | NO |
| 57 | `usrp_crt_by` | varchar(12) | NO |
| 58 | `usrp_crt_date` | datetime | NO |
| 59 | `usrp_mod_times` | int(10,0) | NO |
| 60 | `usrp_mod_by` | varchar(12) | NO |
| 61 | `usrp_mod_date` | datetime | NO |

### `dbo.vch_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vch_company` | varchar(8) | NO |
| 2 | `vch_nbr` | varchar(15) | NO |
| 3 | `vch_date` | datetime | NO |
| 4 | `vch_vt_code` | varchar(15) | NO |
| 5 | `vch_src` | varchar(1) | NO |
| 6 | `vch_src_nbr` | varchar(15) | NO |
| 7 | `vch_doc_cnt` | int(10,0) | NO |
| 8 | `vch_rmks` | varchar(255) | NO |
| 9 | `vch_debit_tot` | numeric(19,8) | NO |
| 10 | `vch_credit_tot` | numeric(19,8) | NO |
| 11 | `vch_delete` | bit | NO |
| 12 | `vch_delete_by` | varchar(12) | NO |
| 13 | `vch_delete_date` | datetime | YES |
| 14 | `vch_export_nbr` | varchar(15) | NO |
| 15 | `vch_csh_obj` | bit | NO |
| 16 | `vch_crt_by` | varchar(12) | NO |
| 17 | `vch_crt_date` | datetime | NO |
| 18 | `vch_mod_times` | int(10,0) | NO |
| 19 | `vch_mod_by` | varchar(12) | NO |
| 20 | `vch_mod_date` | datetime | NO |
| 21 | `vch_pst` | bit | NO |
| 22 | `vch_pst_by` | varchar(12) | NO |
| 23 | `vch_pst_date` | datetime | YES |
| 24 | `vch_chk` | bit | NO |
| 25 | `vch_chk_by` | varchar(12) | NO |
| 26 | `vch_chk_date` | datetime | YES |
| 27 | `vch_char1` | varchar(255) | NO |
| 28 | `vch_char2` | varchar(255) | NO |
| 29 | `vch_char3` | varchar(255) | NO |
| 30 | `vch_char4` | varchar(255) | NO |
| 31 | `vch_char5` | varchar(255) | NO |
| 32 | `vch_char6` | varchar(255) | NO |
| 33 | `vch_qty1` | numeric(19,8) | NO |
| 34 | `vch_qty2` | numeric(19,8) | NO |
| 35 | `vch_crt_name` | varchar(30) | NO |
| 36 | `vch_mod_name` | varchar(30) | NO |
| 37 | `vch_pst_name` | varchar(30) | NO |
| 38 | `vch_chk_name` | varchar(30) | NO |
| 39 | `vch_delete_name` | varchar(30) | NO |

### `dbo.vchd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vchd_company` | varchar(8) | NO |
| 2 | `vchd_nbr` | varchar(15) | NO |
| 3 | `vchd_line` | int(10,0) | NO |
| 4 | `vchd_ac_code` | varchar(15) | NO |
| 5 | `vchd_content` | varchar(255) | NO |
| 6 | `vchd_curr` | varchar(4) | NO |
| 7 | `vchd_ex_rate` | decimal(19,8) | NO |
| 8 | `vchd_price` | decimal(19,8) | NO |
| 9 | `vchd_debit_amt` | numeric(19,8) | NO |
| 10 | `vchd_debit_base` | numeric(19,8) | NO |
| 11 | `vchd_debit_qty` | numeric(19,8) | NO |
| 12 | `vchd_credit_amt` | numeric(19,8) | NO |
| 13 | `vchd_credit_base` | numeric(19,8) | NO |
| 14 | `vchd_credit_qty` | numeric(19,8) | NO |
| 15 | `vchd_dept` | varchar(10) | NO |
| 16 | `vchd_vt_code1` | varchar(30) | NO |
| 17 | `vchd_vt_name1` | varchar(255) | NO |
| 18 | `vchd_vt_code2` | varchar(30) | NO |
| 19 | `vchd_vt_name2` | varchar(255) | NO |
| 20 | `vchd_vt_code3` | varchar(30) | NO |
| 21 | `vchd_vt_name3` | varchar(255) | NO |
| 22 | `vchd_vt_code4` | varchar(30) | NO |
| 23 | `vchd_vt_name4` | varchar(255) | NO |
| 24 | `vchd_due` | bit | NO |
| 25 | `vchd_checked` | bit | NO |
| 26 | `vchd_autochk` | bit | NO |
| 27 | `vchd_settle` | varchar(30) | NO |
| 28 | `vchd_settle_no` | varchar(50) | NO |
| 29 | `vchd_settle_date` | datetime | YES |
| 30 | `vchd_cash_item` | varchar(30) | NO |
| 31 | `vchd_rmks` | varchar(255) | NO |
| 32 | `vchd_crt_by` | varchar(12) | NO |
| 33 | `vchd_crt_date` | datetime | NO |
| 34 | `vchd_mod_times` | int(10,0) | NO |
| 35 | `vchd_mod_by` | varchar(12) | NO |
| 36 | `vchd_mod_date` | datetime | NO |
| 37 | `vchd_char1` | varchar(255) | NO |
| 38 | `vchd_char2` | varchar(255) | NO |
| 39 | `vchd_char3` | varchar(255) | NO |
| 40 | `vchd_char4` | varchar(255) | NO |
| 41 | `vchd_char5` | varchar(255) | NO |
| 42 | `vchd_char6` | varchar(255) | NO |
| 43 | `vchd_qty1` | numeric(19,8) | NO |
| 44 | `vchd_qty2` | numeric(19,8) | NO |
| 45 | `vchd_capf_flow` | int(10,0) | NO |
| 46 | `vchd_src_prog` | varchar(12) | NO |
| 47 | `vchd_src_nbr` | varchar(15) | NO |
| 48 | `vchd_crt_name` | varchar(30) | NO |
| 49 | `vchd_mod_name` | varchar(30) | NO |

### `dbo.vd_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vd_addr` | varchar(8) | NO |
| 2 | `vd_name` | varchar(255) | NO |
| 3 | `vd_sort` | varchar(50) | NO |
| 4 | `vd_txt` | varchar(255) | NO |
| 5 | `vd_attn` | varchar(24) | NO |
| 6 | `vd_tele` | varchar(50) | NO |
| 7 | `vd_fax` | varchar(50) | NO |
| 8 | `vd_email` | varchar(50) | NO |
| 9 | `vd_attn2` | varchar(24) | NO |
| 10 | `vd_tele2` | varchar(50) | NO |
| 11 | `vd_fax2` | varchar(50) | NO |
| 12 | `vd_email2` | varchar(50) | NO |
| 13 | `vd_www` | varchar(80) | NO |
| 14 | `vd_rmks` | varchar(255) | NO |
| 15 | `vd_buyer` | varchar(12) | NO |
| 16 | `vd_curr` | varchar(4) | NO |
| 17 | `vd_vat` | decimal(19,8) | NO |
| 18 | `vd_cr_terms` | varchar(10) | NO |
| 19 | `vd_spare_pct` | decimal(19,8) | NO |
| 20 | `vd_tol_pct` | decimal(19,8) | NO |
| 21 | `vd_service` | int(10,0) | NO |
| 22 | `vd_quot_type` | varchar(1) | NO |
| 23 | `vd_inv_type` | varchar(1) | NO |
| 24 | `vd_vat_method` | varchar(1) | NO |
| 25 | `vd_kind` | varchar(1) | NO |
| 26 | `vd_bid_settle` | bit | NO |
| 27 | `vd_reg_code` | varchar(30) | NO |
| 28 | `vd_bank` | varchar(255) | NO |
| 29 | `vd_bank_acct` | varchar(30) | NO |
| 30 | `vd_comp_owner` | varchar(30) | NO |
| 31 | `vd_reg_fund` | decimal(19,8) | NO |
| 32 | `vd_tunrover` | decimal(19,8) | NO |
| 33 | `vd_open_date` | datetime | YES |
| 34 | `vd_employees` | int(10,0) | NO |
| 35 | `vd_hold` | bit | NO |
| 36 | `vd_ap_ac` | varchar(15) | NO |
| 37 | `vd_tap_ac` | varchar(15) | NO |
| 38 | `vd_sub_ac` | varchar(15) | NO |
| 39 | `vd_comm_ac` | varchar(15) | NO |
| 40 | `vd_wf_status` | varchar(1) | NO |
| 41 | `vd_crt_by` | varchar(12) | NO |
| 42 | `vd_crt_date` | datetime | NO |
| 43 | `vd_mod_times` | int(10,0) | NO |
| 44 | `vd_mod_by` | varchar(12) | NO |
| 45 | `vd_mod_date` | datetime | NO |
| 46 | `vd_pst` | bit | NO |
| 47 | `vd_pst_by` | varchar(12) | NO |
| 48 | `vd_pst_date` | datetime | YES |
| 49 | `vd_char1` | varchar(255) | NO |
| 50 | `vd_char2` | varchar(255) | NO |
| 51 | `vd_char3` | varchar(255) | NO |
| 52 | `vd_char4` | varchar(255) | NO |
| 53 | `vd_char5` | varchar(255) | NO |
| 54 | `vd_char6` | varchar(255) | NO |
| 55 | `vd_qty1` | decimal(19,8) | NO |
| 56 | `vd_qty2` | decimal(19,8) | NO |
| 57 | `vd_invalid` | varchar(1) | NO |
| 58 | `vd_invalid_by` | varchar(12) | NO |
| 59 | `vd_invalid_date` | datetime | YES |
| 60 | `vd_mtl_sales` | varchar(30) | NO |
| 61 | `vd_mtl_rate` | numeric(19,8) | NO |
| 62 | `vd_allow` | bit | NO |
| 63 | `vd_allow_by` | varchar(12) | NO |
| 64 | `vd_allow_date` | datetime | YES |
| 65 | `vd_3c` | bit | NO |
| 66 | `vd_open` | bit | NO |
| 67 | `vd_isinternal` | bit | NO |
| 68 | `vd_strategic` | varchar(1) | NO |

### `dbo.vdad_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vdad_nbr` | varchar(15) | NO |
| 2 | `vdad_vend` | varchar(8) | NO |
| 3 | `vdad_score_last` | numeric(19,8) | NO |
| 4 | `vdad_score_calc` | numeric(19,8) | NO |
| 5 | `vdad_score_fin` | numeric(19,8) | NO |
| 6 | `vdad_selected` | bit | NO |
| 7 | `vdad_updated` | bit | NO |
| 8 | `vdad_has_rcvd` | bit | NO |
| 9 | `vdad_score1` | numeric(19,8) | NO |
| 10 | `vdad_score2` | numeric(19,8) | NO |
| 11 | `vdad_score3` | numeric(19,8) | NO |
| 12 | `vdad_score4` | numeric(19,8) | NO |
| 13 | `vdad_score5` | numeric(19,8) | NO |
| 14 | `vdad_score6` | numeric(19,8) | NO |
| 15 | `vdad_rmks` | varchar(255) | NO |
| 16 | `vdad_crt_by` | varchar(12) | NO |
| 17 | `vdad_crt_date` | datetime | NO |
| 18 | `vdad_mod_times` | int(10,0) | NO |
| 19 | `vdad_mod_by` | varchar(12) | NO |
| 20 | `vdad_mod_date` | datetime | NO |
| 21 | `vdad_char1` | varchar(255) | NO |
| 22 | `vdad_char2` | varchar(255) | NO |
| 23 | `vdad_char3` | varchar(255) | NO |
| 24 | `vdad_char4` | varchar(255) | NO |
| 25 | `vdad_char5` | varchar(255) | NO |
| 26 | `vdad_char6` | varchar(255) | NO |
| 27 | `vdad_qty1` | decimal(19,8) | NO |
| 28 | `vdad_qty2` | decimal(19,8) | NO |

### `dbo.vdpr_hist` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vdpr_year` | int(10,0) | NO |
| 2 | `vdpr_month` | int(10,0) | NO |
| 3 | `vdpr_vend` | varchar(8) | NO |
| 4 | `vdpr_rate` | numeric(19,8) | NO |
| 5 | `vdpr_crt_by` | varchar(12) | NO |
| 6 | `vdpr_crt_date` | datetime | NO |
| 7 | `vdpr_char1` | varchar(255) | NO |
| 8 | `vdpr_char2` | varchar(255) | NO |
| 9 | `vdpr_char3` | varchar(255) | NO |
| 10 | `vdpr_char4` | varchar(255) | NO |
| 11 | `vdpr_char5` | varchar(255) | NO |
| 12 | `vdpr_char6` | varchar(255) | NO |
| 13 | `vdpr_qty1` | decimal(19,8) | NO |
| 14 | `vdpr_qty2` | decimal(19,8) | NO |

### `dbo.vp_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vp_part` | varchar(30) | NO |
| 2 | `vp_vend` | varchar(8) | NO |
| 3 | `vp_vend_part` | varchar(30) | NO |
| 4 | `vp_mfg_part` | varchar(30) | NO |
| 5 | `vp_um` | varchar(4) | NO |
| 6 | `vp_um_rate_m` | decimal(19,8) | NO |
| 7 | `vp_um_rate_d` | decimal(19,8) | NO |
| 8 | `vp_vend_lead` | int(10,0) | NO |
| 9 | `vp_rmks` | varchar(255) | NO |
| 10 | `vp_crt_by` | varchar(12) | NO |
| 11 | `vp_crt_date` | datetime | NO |
| 12 | `vp_mod_times` | int(10,0) | NO |
| 13 | `vp_mod_by` | varchar(12) | NO |
| 14 | `vp_mod_date` | datetime | NO |
| 15 | `vp_pst` | bit | NO |
| 16 | `vp_pst_by` | varchar(12) | NO |
| 17 | `vp_pst_date` | datetime | YES |
| 18 | `vp_char1` | varchar(255) | NO |
| 19 | `vp_char2` | varchar(255) | NO |
| 20 | `vp_char3` | varchar(255) | NO |
| 21 | `vp_char4` | varchar(255) | NO |
| 22 | `vp_char5` | varchar(255) | NO |
| 23 | `vp_char6` | varchar(255) | NO |
| 24 | `vp_qty1` | decimal(19,8) | NO |
| 25 | `vp_qty2` | decimal(19,8) | NO |
| 26 | `vp_end` | datetime | YES |

### `dbo.vq_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vq_part` | varchar(30) | NO |
| 2 | `vq_start` | datetime | NO |
| 3 | `vq_expire` | datetime | NO |
| 4 | `vq_vendor1` | varchar(8) | NO |
| 5 | `vq_vendor2` | varchar(8) | NO |
| 6 | `vq_vendor3` | varchar(8) | NO |
| 7 | `vq_vendor4` | varchar(8) | NO |
| 8 | `vq_vendor5` | varchar(8) | NO |
| 9 | `vq_quota1` | decimal(19,8) | NO |
| 10 | `vq_quota2` | decimal(19,8) | NO |
| 11 | `vq_quota3` | decimal(19,8) | NO |
| 12 | `vq_quota4` | decimal(19,8) | NO |
| 13 | `vq_quota5` | decimal(19,8) | NO |
| 14 | `vq_site` | varchar(8) | NO |
| 15 | `vq_crt_by` | varchar(12) | NO |
| 16 | `vq_crt_date` | datetime | NO |
| 17 | `vq_pst` | bit | NO |
| 18 | `vq_pst_by` | varchar(12) | NO |
| 19 | `vq_pst_date` | datetime | YES |
| 20 | `vq_char1` | varchar(255) | NO |
| 21 | `vq_char2` | varchar(255) | NO |
| 22 | `vq_char3` | varchar(255) | NO |
| 23 | `vq_char4` | varchar(255) | NO |
| 24 | `vq_char5` | varchar(255) | NO |
| 25 | `vq_char6` | varchar(255) | NO |
| 26 | `vq_qty1` | decimal(19,8) | NO |
| 27 | `vq_qty2` | decimal(19,8) | NO |

### `dbo.vt_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vt_code` | varchar(15) | NO |
| 2 | `vt_name` | varchar(50) | NO |
| 3 | `vt_type` | varchar(1) | NO |
| 4 | `vt_sub_type` | varchar(2) | NO |
| 5 | `vt_code_rule` | varchar(15) | NO |
| 6 | `vt_auto_pst` | bit | NO |
| 7 | `vt_d_inc` | varchar(255) | NO |
| 8 | `vt_c_inc` | varchar(255) | NO |
| 9 | `vt_dc_inc` | varchar(255) | NO |
| 10 | `vt_d_exc` | varchar(255) | NO |
| 11 | `vt_c_exc` | varchar(255) | NO |
| 12 | `vt_dc_exc` | varchar(255) | NO |
| 13 | `vt_crt_by` | varchar(12) | NO |
| 14 | `vt_crt_date` | datetime | NO |
| 15 | `vt_mod_times` | int(10,0) | NO |
| 16 | `vt_mod_by` | varchar(12) | NO |
| 17 | `vt_mod_date` | datetime | NO |
| 18 | `vt_char1` | varchar(255) | NO |
| 19 | `vt_char2` | varchar(255) | NO |
| 20 | `vt_char3` | varchar(255) | NO |
| 21 | `vt_char4` | varchar(255) | NO |
| 22 | `vt_char5` | varchar(255) | NO |
| 23 | `vt_char6` | varchar(255) | NO |
| 24 | `vt_qty1` | decimal(19,8) | NO |
| 25 | `vt_qty2` | decimal(19,8) | NO |
| 26 | `vt_sort` | varchar(50) | NO |

### `dbo.wc_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wc_wkctr` | varchar(8) | NO |
| 2 | `wc_desc` | varchar(50) | NO |
| 3 | `wc_dept` | varchar(10) | NO |
| 4 | `wc_men_qty` | numeric(19,8) | NO |
| 5 | `wc_mch_qty` | numeric(19,8) | NO |
| 6 | `wc_lbr_rate` | decimal(19,8) | NO |
| 7 | `wc_bdn_rate` | decimal(19,8) | NO |
| 8 | `wc_crt_by` | varchar(12) | NO |
| 9 | `wc_crt_date` | datetime | NO |
| 10 | `wc_mod_times` | int(10,0) | NO |
| 11 | `wc_mod_by` | varchar(12) | NO |
| 12 | `wc_mod_date` | datetime | NO |
| 13 | `wc_char1` | varchar(255) | NO |
| 14 | `wc_char2` | varchar(255) | NO |
| 15 | `wc_char3` | varchar(255) | NO |
| 16 | `wc_char4` | varchar(255) | NO |
| 17 | `wc_char5` | varchar(255) | NO |
| 18 | `wc_char6` | varchar(255) | NO |
| 19 | `wc_qty1` | decimal(19,8) | NO |
| 20 | `wc_qty2` | decimal(19,8) | NO |
| 21 | `wc_data_src` | varchar(1) | NO |
| 22 | `wc_data_id` | varchar(255) | NO |

### `dbo.wcm_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wcm_site` | varchar(8) | NO |
| 2 | `wcm_wkctr` | varchar(8) | NO |
| 3 | `wcm_year` | int(10,0) | NO |
| 4 | `wcm_month` | int(10,0) | NO |
| 5 | `wcm_lbr_tot` | numeric(19,8) | NO |
| 6 | `wcm_bdn_tot` | numeric(19,8) | NO |
| 7 | `wcm_lbr_hrs` | decimal(19,8) | NO |
| 8 | `wcm_lbr_rate` | decimal(19,8) | NO |
| 9 | `wcm_bdn_rate` | decimal(19,8) | NO |
| 10 | `wcm_lbr_stdrate` | decimal(19,8) | NO |
| 11 | `wcm_bdn_stdrate` | decimal(19,8) | NO |
| 12 | `wcm_crt_by` | varchar(12) | NO |
| 13 | `wcm_crt_date` | datetime | NO |
| 14 | `wcm_mod_times` | int(10,0) | NO |
| 15 | `wcm_mod_by` | varchar(12) | NO |
| 16 | `wcm_mod_date` | datetime | NO |
| 17 | `wcm_char1` | varchar(255) | NO |
| 18 | `wcm_char2` | varchar(255) | NO |
| 19 | `wcm_char3` | varchar(255) | NO |
| 20 | `wcm_char4` | varchar(255) | NO |
| 21 | `wcm_char5` | varchar(255) | NO |
| 22 | `wcm_char6` | varchar(255) | NO |
| 23 | `wcm_qty1` | decimal(19,8) | NO |
| 24 | `wcm_qty2` | decimal(19,8) | NO |

### `dbo.wo_import` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `woim_nbr` | varchar(15) | NO |
| 2 | `woim_lot` | varchar(18) | NO |
| 3 | `woim_date` | datetime | NO |
| 4 | `woim_line` | varchar(8) | NO |
| 5 | `woim_part` | varchar(30) | NO |
| 6 | `woim_qty_ord` | numeric(19,8) | NO |
| 7 | `woim_status` | varchar(1) | NO |
| 8 | `woim_rel_date` | datetime | NO |
| 9 | `woim_due_date` | datetime | NO |
| 10 | `woim_crt_by` | varchar(12) | NO |
| 11 | `woim_crt_date` | datetime | NO |

### `dbo.wo_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wo_nbr` | varchar(15) | NO |
| 2 | `wo_lot` | varchar(18) | NO |
| 3 | `wo_type` | varchar(1) | NO |
| 4 | `wo_type2` | varchar(1) | NO |
| 5 | `wo_part` | varchar(30) | NO |
| 6 | `wo_qty_ord` | numeric(19,8) | NO |
| 7 | `wo_qty_comp` | numeric(19,8) | NO |
| 8 | `wo_qty_rjct` | numeric(19,8) | NO |
| 9 | `wo_line` | varchar(8) | NO |
| 10 | `wo_ord_date` | datetime | NO |
| 11 | `wo_rel_date` | datetime | NO |
| 12 | `wo_due_date` | datetime | NO |
| 13 | `wo_close_by` | varchar(12) | NO |
| 14 | `wo_close_date` | datetime | YES |
| 15 | `wo_status` | varchar(1) | NO |
| 16 | `wo_so_nbr` | varchar(15) | NO |
| 17 | `wo_so_line` | int(10,0) | NO |
| 18 | `wo_fgov_per` | decimal(19,8) | NO |
| 19 | `wo_rmks` | varchar(255) | NO |
| 20 | `wo_other_rmks` | text(2147483647) | YES |
| 21 | `wo_site` | varchar(8) | NO |
| 22 | `wo_wf_staus` | varchar(1) | NO |
| 23 | `wo_prog_code` | varchar(12) | NO |
| 24 | `wo_doc_code` | varchar(12) | NO |
| 25 | `wo_crt_by` | varchar(12) | NO |
| 26 | `wo_crt_date` | datetime | NO |
| 27 | `wo_mod_times` | int(10,0) | NO |
| 28 | `wo_mod_by` | varchar(12) | NO |
| 29 | `wo_mod_date` | datetime | NO |
| 30 | `wo_char1` | varchar(255) | NO |
| 31 | `wo_char2` | varchar(255) | NO |
| 32 | `wo_char3` | varchar(255) | NO |
| 33 | `wo_char4` | varchar(255) | NO |
| 34 | `wo_char5` | varchar(255) | NO |
| 35 | `wo_char6` | varchar(255) | NO |
| 36 | `wo_qty1` | decimal(19,8) | NO |
| 37 | `wo_qty2` | decimal(19,8) | NO |
| 38 | `wo_src` | varchar(2) | NO |
| 39 | `wo_src_nbr` | varchar(15) | NO |
| 40 | `wo_src_lot` | varchar(18) | NO |
| 41 | `wo_sod_conf` | bit | NO |
| 42 | `wo_sod_conf_by` | varchar(12) | NO |
| 43 | `wo_sod_conf_date` | datetime | YES |
| 44 | `wo_close_reason` | varchar(255) | NO |
| 45 | `wo_data_src` | varchar(1) | NO |
| 46 | `wo_data_id` | varchar(255) | NO |
| 47 | `wo_seq` | varchar(15) | NO |

### `dbo.wo_mstr3` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wo3_user_id` | varchar(12) | NO |
| 2 | `wo3_select` | bit | NO |
| 3 | `wo3_class` | int(10,0) | NO |
| 4 | `wo3_alloc` | bit | NO |
| 5 | `wo3_site` | varchar(8) | NO |
| 6 | `wo3_nbr` | varchar(15) | NO |
| 7 | `wo3_lot` | varchar(18) | NO |
| 8 | `wo3_part` | varchar(30) | NO |
| 9 | `wo3_qty_ord` | numeric(19,8) | NO |
| 10 | `wo3_qty_comp` | numeric(19,8) | NO |
| 11 | `wo3_due_date` | datetime | NO |
| 12 | `wo3_rel_date` | datetime | NO |
| 13 | `wo3_so_nbr` | varchar(15) | NO |
| 14 | `wo3_line` | varchar(8) | NO |
| 15 | `wo3_status` | varchar(1) | NO |

### `dbo.woadj_import` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `woadj_nbr` | varchar(15) | NO |
| 2 | `woadj_date` | datetime | NO |
| 3 | `woadj_checker` | varchar(12) | NO |
| 4 | `woadj_line` | varchar(8) | NO |
| 5 | `woadj_rmks` | varchar(255) | NO |
| 6 | `woadj_crt_by` | varchar(12) | NO |
| 7 | `woadj_crt_date` | datetime | NO |
| 8 | `woadjd_wod_nbr` | varchar(15) | NO |
| 9 | `woadjd_wod_lot` | varchar(18) | NO |
| 10 | `woadjd_wod_seq` | int(10,0) | NO |
| 11 | `woadjd_part` | varchar(30) | NO |
| 12 | `woadjd_qty_rec` | numeric(19,8) | NO |
| 13 | `woadjd_qty_cnt` | numeric(19,8) | NO |
| 14 | `woadjd_reason` | varchar(30) | NO |
| 15 | `woadjd_rmks` | varchar(255) | NO |

### `dbo.woadj_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `woadj_nbr` | varchar(15) | NO |
| 2 | `woadj_date` | datetime | NO |
| 3 | `woadj_checker` | varchar(12) | NO |
| 4 | `woadj_line` | varchar(8) | NO |
| 5 | `woadj_type` | varchar(1) | NO |
| 6 | `woadj_rmks` | varchar(255) | NO |
| 7 | `woadj_site` | varchar(8) | NO |
| 8 | `woadj_wf_status` | varchar(1) | NO |
| 9 | `woadj_prog_code` | varchar(12) | NO |
| 10 | `woadj_doc_code` | varchar(12) | NO |
| 11 | `woadj_crt_by` | varchar(12) | NO |
| 12 | `woadj_crt_date` | datetime | NO |
| 13 | `woadj_mod_times` | int(10,0) | NO |
| 14 | `woadj_mod_by` | varchar(12) | NO |
| 15 | `woadj_mod_date` | datetime | NO |
| 16 | `woadj_pst` | bit | NO |
| 17 | `woadj_pst_by` | varchar(12) | NO |
| 18 | `woadj_pst_date` | datetime | YES |
| 19 | `woadj_char1` | varchar(255) | NO |
| 20 | `woadj_char2` | varchar(255) | NO |
| 21 | `woadj_char3` | varchar(255) | NO |
| 22 | `woadj_char4` | varchar(255) | NO |
| 23 | `woadj_char5` | varchar(255) | NO |
| 24 | `woadj_char6` | varchar(255) | NO |
| 25 | `woadj_qty1` | decimal(19,8) | NO |
| 26 | `woadj_qty2` | decimal(19,8) | NO |

### `dbo.woadjd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `woadjd_nbr` | varchar(15) | NO |
| 2 | `woadjd_line` | int(10,0) | NO |
| 3 | `woadjd_wod_nbr` | varchar(15) | NO |
| 4 | `woadjd_wod_lot` | varchar(18) | NO |
| 5 | `woadjd_wod_seq` | int(10,0) | NO |
| 6 | `woadjd_part` | varchar(30) | NO |
| 7 | `woadjd_qty_rec` | numeric(19,8) | NO |
| 8 | `woadjd_qty_cnt` | numeric(19,8) | NO |
| 9 | `woadjd_qty_diff` | numeric(19,8) | NO |
| 10 | `woadjd_reason` | varchar(30) | NO |
| 11 | `woadjd_rmks` | varchar(255) | NO |
| 12 | `woadjd_crt_by` | varchar(12) | NO |
| 13 | `woadjd_crt_date` | datetime | NO |
| 14 | `woadjd_mod_times` | int(10,0) | NO |
| 15 | `woadjd_mod_by` | varchar(12) | NO |
| 16 | `woadjd_mod_date` | datetime | NO |
| 17 | `woadjd_char1` | varchar(255) | NO |
| 18 | `woadjd_char2` | varchar(255) | NO |
| 19 | `woadjd_char3` | varchar(255) | NO |
| 20 | `woadjd_char4` | varchar(255) | NO |
| 21 | `woadjd_char5` | varchar(255) | NO |
| 22 | `woadjd_char6` | varchar(255) | NO |
| 23 | `woadjd_qty1` | decimal(19,8) | NO |
| 24 | `woadjd_qty2` | decimal(19,8) | NO |

### `dbo.woc_ctrl` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `woc_woc` | int(10,0) | NO |
| 2 | `woc_alloc_sub` | bit | NO |
| 3 | `woc_use_alt` | varchar(80) | NO |
| 4 | `woc_route_ctrl` | bit | NO |
| 5 | `woc_modify_wod` | varchar(80) | NO |
| 6 | `woc_modify_wr` | varchar(80) | NO |
| 7 | `woc_pk_with` | varchar(1) | NO |
| 8 | `woc_pk_mode` | varchar(1) | NO |
| 9 | `woc_pk_first` | bit | NO |
| 10 | `woc_pk_pro` | bit | NO |
| 11 | `woc_pk_pro_out` | bit | NO |
| 12 | `woc_fg_con` | varchar(1) | NO |
| 13 | `woc_fg_sub` | bit | NO |
| 14 | `woc_auto_close_wo` | varchar(1) | NO |
| 15 | `woc_close_delay` | int(10,0) | NO |
| 16 | `woc_close_wo` | varchar(80) | NO |
| 17 | `woc_open_wo` | varchar(80) | NO |
| 18 | `woc_open_wo_c` | varchar(80) | NO |
| 19 | `woc_iss_unlimit` | bit | NO |
| 20 | `woc_iss_special` | bit | NO |
| 21 | `woc_rtn_special` | bit | NO |
| 22 | `woc_rtn_ex_iss` | bit | NO |
| 23 | `woc_no_bom` | varchar(1) | NO |
| 24 | `woc_no_route` | varchar(1) | NO |
| 25 | `woc_char1` | varchar(255) | NO |
| 26 | `woc_char2` | varchar(255) | NO |
| 27 | `woc_char3` | varchar(255) | NO |
| 28 | `woc_char4` | varchar(255) | NO |
| 29 | `woc_char5` | varchar(255) | NO |
| 30 | `woc_char6` | varchar(255) | NO |
| 31 | `woc_qty1` | decimal(19,8) | NO |
| 32 | `woc_qty2` | decimal(19,8) | NO |
| 33 | `woc_pk_then_ovr` | bit | NO |
| 34 | `woc_qa_qc` | bit | NO |
| 35 | `woc_close_wo_with_wip` | varchar(80) | NO |
| 36 | `woc_backflush` | varchar(1) | NO |
| 37 | `woc_backflush_s` | varchar(1) | NO |
| 38 | `woc_auto_ovr` | bit | NO |
| 39 | `woc_backflush_type` | varchar(1) | YES |
| 40 | `woc_ord_mult` | bit | NO |

### `dbo.wod_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wod_nbr` | varchar(15) | NO |
| 2 | `wod_lot` | varchar(18) | NO |
| 3 | `wod_seq` | int(10,0) | NO |
| 4 | `wod_part` | varchar(30) | NO |
| 5 | `wod_loc` | varchar(8) | NO |
| 6 | `wod_op` | int(10,0) | NO |
| 7 | `wod_incl_sub` | bit | NO |
| 8 | `wod_alt` | bit | NO |
| 9 | `wod_alt_seq` | int(10,0) | NO |
| 10 | `wod_roll_iss` | bit | NO |
| 11 | `wod_qty_per_m` | numeric(19,8) | NO |
| 12 | `wod_qty_per_d` | numeric(19,8) | NO |
| 13 | `wod_qty_req_std` | numeric(19,8) | NO |
| 14 | `wod_qty_req_scr` | numeric(19,8) | NO |
| 15 | `wod_qty_req` | numeric(19,8) | NO |
| 16 | `wod_due_date` | datetime | NO |
| 17 | `wod_qty_iss` | numeric(19,8) | NO |
| 18 | `wod_ovr_iss` | numeric(19,8) | NO |
| 19 | `wod_qty_adj` | numeric(19,8) | NO |
| 20 | `wod_qty_rtng` | numeric(19,8) | NO |
| 21 | `wod_qty_rtnv` | numeric(19,8) | NO |
| 22 | `wod_qty_rtns` | numeric(19,8) | NO |
| 23 | `wod_qty_scr` | numeric(19,8) | NO |
| 24 | `wod_qty_con` | numeric(19,8) | NO |
| 25 | `wod_qty_alloc` | numeric(19,8) | NO |
| 26 | `wod_qty_pts_m` | numeric(19,8) | NO |
| 27 | `wod_qty_pts_d` | numeric(19,8) | NO |
| 28 | `wod_mrp` | bit | NO |
| 29 | `wod_rmks` | varchar(255) | NO |
| 30 | `wod_crt_by` | varchar(12) | NO |
| 31 | `wod_crt_date` | datetime | NO |
| 32 | `wod_mod_times` | int(10,0) | NO |
| 33 | `wod_mod_by` | varchar(12) | NO |
| 34 | `wod_mod_date` | datetime | NO |
| 35 | `wod_char1` | varchar(255) | NO |
| 36 | `wod_char2` | varchar(255) | NO |
| 37 | `wod_char3` | varchar(255) | NO |
| 38 | `wod_char4` | varchar(255) | NO |
| 39 | `wod_char5` | varchar(255) | NO |
| 40 | `wod_char6` | varchar(255) | NO |
| 41 | `wod_qty1` | decimal(19,8) | NO |
| 42 | `wod_qty2` | decimal(19,8) | NO |
| 43 | `wod_sodb_seq` | int(10,0) | NO |
| 44 | `wod_qty_org` | numeric(19,8) | NO |
| 45 | `wod_wire_req` | varchar(1000) | NO |
| 46 | `wod_ps_rmks` | varchar(1000) | NO |
| 47 | `wod_data_src` | varchar(1) | NO |
| 48 | `wod_data_id` | varchar(255) | NO |

### `dbo.wod_det1` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wod1_userid` | varchar(12) | NO |
| 2 | `wod1_select` | bit | NO |
| 3 | `wod1_type_pr` | varchar(1) | NO |
| 4 | `wod1_nbr` | varchar(15) | NO |
| 5 | `wod1_lot` | varchar(18) | NO |
| 6 | `wod1_seq` | int(10,0) | NO |
| 7 | `wod1_part` | varchar(30) | NO |
| 8 | `wod1_qty_req` | numeric(19,8) | NO |
| 9 | `wod1_qty_iss` | numeric(19,8) | NO |
| 10 | `wod1_qty_rtn_gv` | numeric(19,8) | NO |
| 11 | `wod1_qty_req_net` | numeric(19,8) | NO |
| 12 | `wod1_qty_req_total` | numeric(19,8) | NO |
| 13 | `wod1_qty_req_open` | numeric(19,8) | NO |
| 14 | `wod1_sfty_stk` | numeric(19,8) | NO |
| 15 | `wod1_qty_remain` | numeric(19,8) | NO |
| 16 | `wod1_qty_alloc` | numeric(19,8) | NO |
| 17 | `wod1_qty_short` | numeric(19,8) | NO |
| 18 | `wod1_qty_oh` | numeric(19,8) | NO |
| 19 | `wod1_qty_unalloc` | numeric(19,8) | NO |
| 20 | `wod1_qty_on_order` | numeric(19,8) | NO |
| 21 | `wod1_qty_pr_org` | numeric(19,8) | NO |
| 22 | `wod1_qty_pr` | numeric(19,8) | NO |
| 23 | `wod1_due_date` | datetime | NO |
| 24 | `wod1_rmks` | varchar(255) | NO |
| 25 | `wod1_par` | varchar(30) | NO |
| 26 | `wod1_exp` | bit | NO |
| 27 | `wod1_qty_suggested` | numeric(19,8) | NO |
| 28 | `wod1_wo_line` | varchar(8) | NO |
| 29 | `wod1_rel_date` | datetime | YES |

### `dbo.wod_det3` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wod3_user_id` | varchar(12) | NO |
| 2 | `wod3_site` | varchar(8) | NO |
| 3 | `wod3_nbr` | varchar(15) | NO |
| 4 | `wod3_lot` | varchar(18) | NO |
| 5 | `wod3_seq` | int(10,0) | NO |
| 6 | `wod3_part` | varchar(30) | NO |
| 7 | `wod3_due_date` | datetime | NO |
| 8 | `wod3_qty_req` | numeric(19,8) | NO |
| 9 | `wod3_qty_iss` | numeric(19,8) | NO |
| 10 | `wod3_qty_rtngv` | numeric(19,8) | NO |
| 11 | `wod3_qty_net` | numeric(19,8) | NO |
| 12 | `wod3_qty_alloc` | numeric(19,8) | NO |
| 13 | `wod3_qty_short` | numeric(19,8) | NO |
| 14 | `wod3_qty_oh` | numeric(19,8) | NO |
| 15 | `wod3_qty_unalloc` | numeric(19,8) | NO |
| 16 | `wod3_qty_ord` | numeric(19,8) | NO |

### `dbo.wol_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wol_wkctr` | varchar(8) | NO |
| 2 | `wol_wo_nbr` | varchar(15) | NO |
| 3 | `wol_wo_lot` | varchar(18) | NO |
| 4 | `wol_part` | varchar(30) | NO |
| 5 | `wol_date` | datetime | NO |
| 6 | `wol_lbr_hrs` | decimal(19,8) | NO |
| 7 | `wol_crt_by` | varchar(12) | NO |
| 8 | `wol_crt_date` | datetime | NO |
| 9 | `wol_mod_times` | int(10,0) | NO |
| 10 | `wol_mod_by` | varchar(12) | NO |
| 11 | `wol_mod_date` | datetime | NO |
| 12 | `wol_char1` | varchar(255) | NO |
| 13 | `wol_char2` | varchar(255) | NO |
| 14 | `wol_char3` | varchar(255) | NO |
| 15 | `wol_char4` | varchar(255) | NO |
| 16 | `wol_char5` | varchar(255) | NO |
| 17 | `wol_char6` | varchar(255) | NO |
| 18 | `wol_qty1` | decimal(19,8) | NO |
| 19 | `wol_qty2` | decimal(19,8) | NO |

### `dbo.wom_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wom_year` | int(10,0) | NO |
| 2 | `wom_month` | int(10,0) | NO |
| 3 | `wom_wo_nbr` | varchar(15) | NO |
| 4 | `wom_wo_lot` | varchar(18) | NO |
| 5 | `wom_part` | varchar(30) | NO |
| 6 | `wom_beg_wipmtl` | numeric(19,8) | NO |
| 7 | `wom_beg_wiplbr` | numeric(19,8) | NO |
| 8 | `wom_beg_amt` | numeric(19,8) | NO |
| 9 | `wom_beg_mtl` | numeric(19,8) | NO |
| 10 | `wom_beg_lbr` | numeric(19,8) | NO |
| 11 | `wom_beg_bdn` | numeric(19,8) | NO |
| 12 | `wom_beg_sub` | numeric(19,8) | NO |
| 13 | `wom_beg_mtlll` | numeric(19,8) | NO |
| 14 | `wom_beg_lbrll` | numeric(19,8) | NO |
| 15 | `wom_beg_bdnll` | numeric(19,8) | NO |
| 16 | `wom_beg_subll` | numeric(19,8) | NO |
| 17 | `wom_stkin_qty` | numeric(19,8) | NO |
| 18 | `wom_subin_qty` | numeric(19,8) | NO |
| 19 | `wom_cur_amt` | numeric(19,8) | NO |
| 20 | `wom_cur_mtl` | numeric(19,8) | NO |
| 21 | `wom_cur_lbr` | numeric(19,8) | NO |
| 22 | `wom_cur_bdn` | numeric(19,8) | NO |
| 23 | `wom_cur_sub` | numeric(19,8) | NO |
| 24 | `wom_cur_mtlll` | numeric(19,8) | NO |
| 25 | `wom_cur_lbrll` | numeric(19,8) | NO |
| 26 | `wom_cur_bdnll` | numeric(19,8) | NO |
| 27 | `wom_cur_subll` | numeric(19,8) | NO |
| 28 | `wom_lock` | bit | NO |
| 29 | `wom_end_wipmtl` | numeric(19,8) | NO |
| 30 | `wom_end_wiplbr` | numeric(19,8) | NO |
| 31 | `wom_end_amt` | numeric(19,8) | NO |
| 32 | `wom_end_mtl` | numeric(19,8) | NO |
| 33 | `wom_end_lbr` | numeric(19,8) | NO |
| 34 | `wom_end_bdn` | numeric(19,8) | NO |
| 35 | `wom_end_sub` | numeric(19,8) | NO |
| 36 | `wom_end_mtlll` | numeric(19,8) | NO |
| 37 | `wom_end_lbrll` | numeric(19,8) | NO |
| 38 | `wom_end_bdnll` | numeric(19,8) | NO |
| 39 | `wom_end_subll` | numeric(19,8) | NO |
| 40 | `wom_crt_by` | varchar(12) | NO |
| 41 | `wom_crt_date` | datetime | NO |
| 42 | `wom_mod_times` | int(10,0) | NO |
| 43 | `wom_mod_by` | varchar(12) | NO |
| 44 | `wom_mod_date` | datetime | NO |
| 45 | `wom_char1` | varchar(255) | NO |
| 46 | `wom_char2` | varchar(255) | NO |
| 47 | `wom_char3` | varchar(255) | NO |
| 48 | `wom_char4` | varchar(255) | NO |
| 49 | `wom_char5` | varchar(255) | NO |
| 50 | `wom_char6` | varchar(255) | NO |
| 51 | `wom_qty1` | decimal(19,8) | NO |
| 52 | `wom_qty2` | decimal(19,8) | NO |

### `dbo.wr_bak_20260120` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wr_nbr` | varchar(15) | NO |
| 2 | `wr_lot` | varchar(18) | NO |
| 3 | `wr_op` | int(10,0) | NO |
| 4 | `wr_desc` | varchar(100) | NO |
| 5 | `wr_wkctr` | varchar(8) | NO |
| 6 | `wr_qty_ord` | numeric(19,8) | NO |
| 7 | `wr_qty_comp` | numeric(19,8) | NO |
| 8 | `wr_run_act` | numeric(19,8) | NO |
| 9 | `wr_qty_rjct` | numeric(19,8) | NO |
| 10 | `wr_yield_pct` | decimal(19,8) | NO |
| 11 | `wr_tool` | varchar(80) | NO |
| 12 | `wr_param` | varchar(255) | NO |
| 13 | `wr_start` | datetime | NO |
| 14 | `wr_due` | datetime | NO |
| 15 | `wr_run` | numeric(19,8) | NO |
| 16 | `wr_prod_rate` | numeric(19,8) | NO |
| 17 | `wr_um` | varchar(1) | NO |
| 18 | `wr_rmks` | varchar(255) | NO |
| 19 | `wr_crt_by` | varchar(12) | NO |
| 20 | `wr_crt_date` | datetime | NO |
| 21 | `wr_mod_times` | int(10,0) | NO |
| 22 | `wr_mod_by` | varchar(12) | NO |
| 23 | `wr_mod_date` | datetime | NO |
| 24 | `wr_char1` | varchar(255) | NO |
| 25 | `wr_char2` | varchar(255) | NO |
| 26 | `wr_char3` | varchar(255) | NO |
| 27 | `wr_char4` | varchar(255) | NO |
| 28 | `wr_char5` | varchar(255) | NO |
| 29 | `wr_char6` | varchar(255) | NO |
| 30 | `wr_qty1` | decimal(19,8) | NO |
| 31 | `wr_qty2` | decimal(19,8) | NO |
| 32 | `wr_alt` | bit | NO |
| 33 | `wr_alt_op` | int(10,0) | NO |
| 34 | `wr_s_price` | decimal(19,8) | NO |
| 35 | `wr_s_price_vat` | decimal(19,8) | NO |
| 36 | `wr_vend` | varchar(8) | NO |
| 37 | `wr_vat` | numeric(19,8) | NO |
| 38 | `wr_um_rate` | numeric(19,8) | NO |
| 39 | `wr_data_src` | varchar(1) | NO |
| 40 | `wr_data_id` | varchar(255) | NO |
| 41 | `wr_first` | bit | NO |
| 42 | `wr_op_type` | varchar(30) | NO |
| 43 | `wr_equ` | bit | NO |
| 44 | `wr_mou` | bit | NO |
| 45 | `wr_usr` | bit | NO |
| 46 | `wr_part` | varchar(30) | NO |
| 47 | `wr_att` | bit | NO |
| 48 | `wr_devices` | varchar(15) | NO |
| 49 | `wr_type` | varchar(1) | NO |
| 50 | `wr_po_part` | varchar(30) | NO |

### `dbo.wr_route` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wr_nbr` | varchar(15) | NO |
| 2 | `wr_lot` | varchar(18) | NO |
| 3 | `wr_op` | int(10,0) | NO |
| 4 | `wr_desc` | varchar(100) | NO |
| 5 | `wr_wkctr` | varchar(8) | NO |
| 6 | `wr_qty_ord` | numeric(19,8) | NO |
| 7 | `wr_qty_comp` | numeric(19,8) | NO |
| 8 | `wr_run_act` | numeric(19,8) | NO |
| 9 | `wr_qty_rjct` | numeric(19,8) | NO |
| 10 | `wr_yield_pct` | decimal(19,8) | NO |
| 11 | `wr_tool` | varchar(80) | NO |
| 12 | `wr_param` | varchar(255) | NO |
| 13 | `wr_start` | datetime | NO |
| 14 | `wr_due` | datetime | NO |
| 15 | `wr_run` | numeric(19,8) | NO |
| 16 | `wr_prod_rate` | numeric(19,8) | NO |
| 17 | `wr_um` | varchar(1) | NO |
| 18 | `wr_rmks` | varchar(255) | NO |
| 19 | `wr_crt_by` | varchar(12) | NO |
| 20 | `wr_crt_date` | datetime | NO |
| 21 | `wr_mod_times` | int(10,0) | NO |
| 22 | `wr_mod_by` | varchar(12) | NO |
| 23 | `wr_mod_date` | datetime | NO |
| 24 | `wr_char1` | varchar(255) | NO |
| 25 | `wr_char2` | varchar(255) | NO |
| 26 | `wr_char3` | varchar(255) | NO |
| 27 | `wr_char4` | varchar(255) | NO |
| 28 | `wr_char5` | varchar(255) | NO |
| 29 | `wr_char6` | varchar(255) | NO |
| 30 | `wr_qty1` | decimal(19,8) | NO |
| 31 | `wr_qty2` | decimal(19,8) | NO |
| 32 | `wr_alt` | bit | NO |
| 33 | `wr_alt_op` | int(10,0) | NO |
| 34 | `wr_s_price` | decimal(19,8) | NO |
| 35 | `wr_s_price_vat` | decimal(19,8) | NO |
| 36 | `wr_vend` | varchar(8) | NO |
| 37 | `wr_vat` | numeric(19,8) | NO |
| 38 | `wr_um_rate` | numeric(19,8) | NO |
| 39 | `wr_data_src` | varchar(1) | NO |
| 40 | `wr_data_id` | varchar(255) | NO |
| 41 | `wr_first` | bit | NO |
| 42 | `wr_op_type` | varchar(30) | NO |
| 43 | `wr_equ` | bit | NO |
| 44 | `wr_mou` | bit | NO |
| 45 | `wr_usr` | bit | NO |
| 46 | `wr_part` | varchar(30) | NO |
| 47 | `wr_att` | bit | NO |
| 48 | `wr_devices` | varchar(15) | NO |
| 49 | `wr_type` | varchar(1) | NO |
| 50 | `wr_po_part` | varchar(30) | NO |

### `dbo.wtf_mstr` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wtf_nbr` | varchar(15) | NO |
| 2 | `wtf_date` | datetime | NO |
| 3 | `wtf_wo_line_fr` | varchar(8) | NO |
| 4 | `wtf_wo_line_to` | varchar(8) | NO |
| 5 | `wtf_rmks` | varchar(255) | NO |
| 6 | `wtf_crt_by` | varchar(12) | NO |
| 7 | `wtf_crt_date` | datetime | NO |
| 8 | `wtf_mod_times` | int(10,0) | NO |
| 9 | `wtf_mod_by` | varchar(12) | NO |
| 10 | `wtf_mod_date` | datetime | NO |
| 11 | `wtf_pst` | bit | NO |
| 12 | `wtf_pst_by` | varchar(12) | NO |
| 13 | `wtf_pst_date` | datetime | YES |
| 14 | `wtf_site` | varchar(8) | NO |
| 15 | `wtf_wf_status` | varchar(1) | NO |
| 16 | `wtf_prog_code` | varchar(12) | NO |
| 17 | `wtf_doc_code` | varchar(12) | NO |
| 18 | `wtf_char1` | varchar(255) | NO |
| 19 | `wtf_char2` | varchar(255) | NO |
| 20 | `wtf_char3` | varchar(255) | NO |
| 21 | `wtf_char4` | varchar(255) | NO |
| 22 | `wtf_char5` | varchar(255) | NO |
| 23 | `wtf_char6` | varchar(255) | NO |
| 24 | `wtf_qty1` | decimal(19,8) | NO |
| 25 | `wtf_qty2` | decimal(19,8) | NO |

### `dbo.wtfd_det` (BASE TABLE)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wtfd_nbr` | varchar(15) | NO |
| 2 | `wtfd_line` | int(10,0) | NO |
| 3 | `wtfd_wo_nbr_iss` | varchar(15) | NO |
| 4 | `wtfd_wo_lot_iss` | varchar(18) | NO |
| 5 | `wtfd_wo_seq_iss` | int(10,0) | NO |
| 6 | `wtfd_part` | varchar(30) | NO |
| 7 | `wtfd_qty_req_std` | numeric(19,8) | NO |
| 8 | `wtfd_qty_req_scr` | numeric(19,8) | NO |
| 9 | `wtfd_wo_nbr_rtn` | varchar(15) | NO |
| 10 | `wtfd_wo_lot_rtn` | varchar(18) | NO |
| 11 | `wtfd_wo_seq_rtn` | int(10,0) | NO |
| 12 | `wtfd_qty_wip` | numeric(19,8) | NO |
| 13 | `wtfd_qty_iss` | numeric(19,8) | NO |
| 14 | `wtfd_qty_ovr` | numeric(19,8) | NO |
| 15 | `wtfd_rmks` | varchar(255) | NO |
| 16 | `wtfd_crt_by` | varchar(12) | NO |
| 17 | `wtfd_crt_date` | datetime | NO |
| 18 | `wtfd_mod_times` | int(10,0) | NO |
| 19 | `wtfd_mod_by` | varchar(12) | NO |
| 20 | `wtfd_mod_date` | datetime | NO |
| 21 | `wtfd_char1` | varchar(255) | NO |
| 22 | `wtfd_char2` | varchar(255) | NO |
| 23 | `wtfd_char3` | varchar(255) | NO |
| 24 | `wtfd_char4` | varchar(255) | NO |
| 25 | `wtfd_char5` | varchar(255) | NO |
| 26 | `wtfd_char6` | varchar(255) | NO |
| 27 | `wtfd_qty1` | decimal(19,8) | NO |
| 28 | `wtfd_qty2` | decimal(19,8) | NO |

### `dbo.SDH_HIST_OA_VIEW` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `acc_name` | varchar(50) | YES |
| 2 | `cm_name` | varchar(255) | NO |
| 3 | `pt_desc1` | varchar(255) | NO |
| 4 | `pt_spec` | varchar(255) | NO |
| 5 | `so_char2` | varchar(255) | YES |
| 6 | `gend_property1` | varchar(255) | NO |
| 7 | `gend_property2` | varchar(255) | NO |
| 8 | `sdh_flow_no` | int(10,0) | NO |
| 9 | `sdh_site` | varchar(8) | NO |
| 10 | `sdh_so_nbr` | varchar(15) | NO |
| 11 | `sdh_sod_line` | int(10,0) | NO |
| 12 | `sdh_dn_dn` | varchar(15) | NO |
| 13 | `sdh_dnd_line` | int(10,0) | NO |
| 14 | `sdh_dn_date` | datetime | NO |
| 15 | `sdh_ord_date` | datetime | YES |
| 16 | `sdh_cust` | varchar(8) | NO |
| 17 | `sdh_part` | varchar(30) | NO |
| 18 | `sdh_qty_ord` | numeric(19,8) | NO |
| 19 | `sdh_qty_spare` | numeric(19,8) | NO |
| 20 | `sdh_qty_shp` | numeric(19,8) | NO |
| 21 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 22 | `sdh_um` | varchar(4) | NO |
| 23 | `sdh_um_rate_m` | decimal(19,8) | NO |
| 24 | `sdh_um_rate_d` | decimal(19,8) | NO |
| 25 | `sdh_sod_price` | decimal(19,8) | NO |
| 26 | `sdh_curr` | varchar(4) | NO |
| 27 | `sdh_ex_rate` | decimal(19,8) | NO |
| 28 | `sdh_so_vat` | decimal(19,8) | NO |
| 29 | `sdh_dn_type` | varchar(1) | NO |
| 30 | `sdh_so_slspsn` | varchar(12) | NO |
| 31 | `sdh_cost` | decimal(19,8) | NO |
| 32 | `sdh_crt_by` | varchar(12) | NO |
| 33 | `sdh_crt_date` | datetime | NO |
| 34 | `pl_desc` | varchar(30) | YES |
| 35 | `sdh_sod_price_vat` | decimal(18,2) | YES |

### `dbo.v_ac_name` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ac_code` | varchar(15) | NO |
| 2 | `ac_upper_ac` | varchar(15) | NO |
| 3 | `ac_name` | varchar(50) | NO |
| 4 | `ac_type` | int(10,0) | NO |
| 5 | `ac_category` | int(10,0) | NO |
| 6 | `ac_d_c` | varchar(1) | NO |
| 7 | `ac_curr` | varchar(4) | NO |
| 8 | `ac_dept_req` | bit | NO |
| 9 | `ac_analy1_src` | varchar(1) | NO |
| 10 | `ac_analy1_ctrl` | varchar(1) | NO |
| 11 | `ac_analy2_src` | varchar(1) | NO |
| 12 | `ac_analy2_ctrl` | varchar(1) | NO |
| 13 | `ac_analy3_src` | varchar(1) | NO |
| 14 | `ac_analy3_ctrl` | varchar(1) | NO |
| 15 | `ac_analy4_src` | varchar(1) | NO |
| 16 | `ac_analy4_ctrl` | varchar(1) | NO |
| 17 | `ac_valid` | bit | NO |
| 18 | `ac_qty_control` | bit | NO |
| 19 | `ac_unit` | varchar(4) | NO |
| 20 | `ac_trans` | bit | NO |
| 21 | `ac_inventory` | bit | NO |
| 22 | `ac_daily` | bit | NO |
| 23 | `ac_settle` | bit | NO |
| 24 | `ac_bank_ac` | bit | NO |
| 25 | `ac_cash_ac` | bit | NO |
| 26 | `ac_cashflow` | bit | NO |
| 27 | `ac_cashflow_item` | varchar(4) | NO |
| 28 | `ac_level` | int(10,0) | NO |
| 29 | `ac_crt_by` | varchar(12) | NO |
| 30 | `ac_crt_date` | datetime | NO |
| 31 | `ac_mod_times` | int(10,0) | NO |
| 32 | `ac_mod_by` | varchar(12) | NO |
| 33 | `ac_mod_date` | datetime | NO |
| 34 | `ac_char1` | varchar(255) | NO |
| 35 | `ac_char2` | varchar(255) | NO |
| 36 | `ac_char3` | varchar(255) | NO |
| 37 | `ac_char4` | varchar(255) | NO |
| 38 | `ac_char5` | varchar(255) | NO |
| 39 | `ac_char6` | varchar(255) | NO |
| 40 | `ac_qty1` | decimal(19,8) | NO |
| 41 | `ac_qty2` | decimal(19,8) | NO |
| 42 | `ac_multi_curr` | bit | NO |
| 43 | `ac_view_perm` | varchar(255) | NO |
| 44 | `ac_cashflow_item_c` | varchar(4) | NO |
| 45 | `ac_fullname` | varchar(255) | YES |

### `dbo.v_ap_grnd` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prh_receiver` | varchar(15) | NO |
| 2 | `prh_grnd_line` | int(10,0) | NO |
| 3 | `prh_nbr` | varchar(15) | NO |
| 4 | `prh_line` | int(10,0) | NO |
| 5 | `prh_part` | varchar(30) | NO |
| 6 | `prh_qty_rcvd` | numeric(19,8) | NO |
| 7 | `prh_qty_spare_rcvd` | numeric(19,8) | NO |
| 8 | `prh_um` | varchar(4) | NO |
| 9 | `prh_rcp_date` | datetime | NO |
| 10 | `prh_vend` | varchar(8) | NO |
| 11 | `prh_ps_nbr` | varchar(30) | NO |
| 12 | `pt_desc1` | varchar(255) | NO |
| 13 | `si_company` | varchar(8) | NO |
| 14 | `prh_site` | varchar(8) | NO |
| 15 | `prh_rcp_type` | varchar(1) | NO |
| 16 | `prh_curr` | varchar(4) | NO |
| 17 | `prh_pur_cost` | decimal(19,8) | NO |
| 18 | `prh_vat` | decimal(19,8) | NO |
| 19 | `po_type` | varchar(1) | NO |
| 20 | `apd_qty_pay` | numeric(38,8) | NO |

### `dbo.v_ap_mstr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ap_nbr` | varchar(15) | NO |
| 2 | `ap_date` | datetime | NO |
| 3 | `ap_doc_code` | varchar(15) | NO |
| 4 | `ap_vendor` | varchar(8) | NO |
| 5 | `ap_company` | varchar(8) | NO |
| 6 | `ap_vo_nbr` | varchar(15) | NO |
| 7 | `ap_curr` | varchar(4) | NO |
| 8 | `ap_exch_rate` | decimal(19,8) | NO |
| 9 | `ap_terms` | varchar(10) | NO |
| 10 | `ap_due_date` | datetime | YES |
| 11 | `ap_disc_date` | datetime | YES |
| 12 | `ap_disc_pct` | decimal(19,8) | NO |
| 13 | `ap_inv_type` | varchar(1) | NO |
| 14 | `ap_vat_method` | varchar(1) | NO |
| 15 | `ap_vat_rate` | numeric(19,8) | NO |
| 16 | `ap_inv_nbr` | varchar(255) | NO |
| 17 | `ap_inv_date` | datetime | YES |
| 18 | `ap_inv_amta` | numeric(19,8) | NO |
| 19 | `ap_inv_amtb` | numeric(19,8) | NO |
| 20 | `ap_inv_amt` | numeric(19,8) | NO |
| 21 | `ap_last_exch_rate` | decimal(19,8) | NO |
| 22 | `ap_tot_exch_amt` | numeric(19,8) | NO |
| 23 | `ap_amt` | numeric(19,8) | NO |
| 24 | `ap_curr_amt` | numeric(19,8) | NO |
| 25 | `ap_curr_vat` | numeric(19,8) | NO |
| 26 | `ap_paid_amt` | numeric(19,8) | NO |
| 27 | `ap_base_ap_amt` | numeric(19,8) | NO |
| 28 | `ap_base_amt` | numeric(19,8) | NO |
| 29 | `ap_base_vat_amt` | numeric(19,8) | NO |
| 30 | `ap_rmks` | varchar(255) | NO |
| 31 | `ap_closed` | bit | NO |
| 32 | `ap_hold` | bit | NO |
| 33 | `ap_prt_cnt` | int(10,0) | NO |
| 34 | `ap_prog_code` | varchar(12) | NO |
| 35 | `ap_crt_by` | varchar(12) | NO |
| 36 | `ap_crt_date` | datetime | NO |
| 37 | `ap_mod_times` | int(10,0) | NO |
| 38 | `ap_mod_by` | varchar(12) | NO |
| 39 | `ap_mod_date` | datetime | NO |
| 40 | `ap_pst` | bit | NO |
| 41 | `ap_pst_by` | varchar(12) | NO |
| 42 | `ap_pst_date` | datetime | YES |
| 43 | `ap_char1` | varchar(255) | NO |
| 44 | `ap_char2` | varchar(255) | NO |
| 45 | `ap_char3` | varchar(255) | NO |
| 46 | `ap_char4` | varchar(255) | NO |
| 47 | `ap_char5` | varchar(255) | NO |
| 48 | `ap_char6` | varchar(255) | NO |
| 49 | `ap_qty1` | decimal(19,8) | NO |
| 50 | `ap_qty2` | decimal(19,8) | NO |
| 51 | `vt_code` | varchar(15) | YES |
| 52 | `vt_name` | varchar(50) | YES |
| 53 | `vt_type` | varchar(1) | YES |
| 54 | `vt_sub_type` | varchar(2) | YES |
| 55 | `vt_code_rule` | varchar(15) | YES |
| 56 | `vt_auto_pst` | bit | YES |
| 57 | `vt_d_inc` | varchar(255) | YES |
| 58 | `vt_c_inc` | varchar(255) | YES |
| 59 | `vt_dc_inc` | varchar(255) | YES |
| 60 | `vt_d_exc` | varchar(255) | YES |
| 61 | `vt_c_exc` | varchar(255) | YES |
| 62 | `vt_dc_exc` | varchar(255) | YES |
| 63 | `vt_crt_by` | varchar(12) | YES |
| 64 | `vt_crt_date` | datetime | YES |
| 65 | `vt_mod_times` | int(10,0) | YES |
| 66 | `vt_mod_by` | varchar(12) | YES |
| 67 | `vt_mod_date` | datetime | YES |
| 68 | `vt_char1` | varchar(255) | YES |
| 69 | `vt_char2` | varchar(255) | YES |
| 70 | `vt_char3` | varchar(255) | YES |
| 71 | `vt_char4` | varchar(255) | YES |
| 72 | `vt_char5` | varchar(255) | YES |
| 73 | `vt_char6` | varchar(255) | YES |
| 74 | `vt_qty1` | decimal(19,8) | YES |
| 75 | `vt_qty2` | decimal(19,8) | YES |
| 76 | `vt_sort` | varchar(50) | YES |
| 77 | `apd_src_nbr` | varchar(15) | NO |

### `dbo.v_ap_rtsd` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prh_receiver` | varchar(15) | NO |
| 2 | `prh_grnd_line` | int(10,0) | NO |
| 3 | `prh_nbr` | varchar(15) | NO |
| 4 | `prh_line` | int(10,0) | NO |
| 5 | `prh_part` | varchar(30) | NO |
| 6 | `prh_qty_rcvd` | numeric(19,8) | NO |
| 7 | `prh_qty_spare_rcvd` | numeric(19,8) | NO |
| 8 | `prh_um` | varchar(4) | NO |
| 9 | `prh_rcp_date` | datetime | NO |
| 10 | `prh_vend` | varchar(8) | NO |
| 11 | `prh_ps_nbr` | varchar(30) | NO |
| 12 | `pt_desc1` | varchar(255) | NO |
| 13 | `si_company` | varchar(8) | NO |
| 14 | `prh_site` | varchar(8) | NO |
| 15 | `prh_rcp_type` | varchar(1) | NO |
| 16 | `prh_curr` | varchar(4) | NO |
| 17 | `prh_pur_cost` | decimal(19,8) | NO |
| 18 | `prh_vat` | decimal(19,8) | NO |
| 19 | `po_type` | varchar(1) | NO |
| 20 | `apd_qty_pay` | numeric(38,8) | NO |

### `dbo.v_apd_line` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ap_nbr` | varchar(15) | NO |
| 2 | `ap_date` | datetime | NO |
| 3 | `ap_company` | varchar(8) | NO |
| 4 | `ap_vendor` | varchar(8) | NO |
| 5 | `ap_curr` | varchar(4) | NO |
| 6 | `ap_pst` | bit | NO |
| 7 | `ap_inv_amt` | numeric(19,8) | NO |
| 8 | `ap_amt` | numeric(19,8) | NO |
| 9 | `ap_paid_amt` | numeric(19,8) | NO |
| 10 | `ap_vat_rate` | numeric(19,8) | NO |
| 11 | `apd_nbr` | varchar(15) | NO |
| 12 | `apd_line` | int(10,0) | NO |
| 13 | `apd_src` | varchar(1) | NO |
| 14 | `apd_src_nbr` | varchar(15) | NO |
| 15 | `apd_src_line` | int(10,0) | NO |
| 16 | `apd_src_date` | datetime | YES |
| 17 | `apd_qty_pay` | numeric(19,8) | NO |
| 18 | `apd_src_cost` | decimal(19,8) | NO |
| 19 | `apd_pur_cost` | decimal(19,8) | NO |
| 20 | `apd_minus_amt` | numeric(19,8) | NO |
| 21 | `apd_ap_amt` | numeric(19,8) | NO |
| 22 | `apd_curr_amt` | numeric(19,8) | NO |
| 23 | `apd_curr_vat` | numeric(19,8) | NO |
| 24 | `apd_base_ap_amt` | numeric(19,8) | NO |
| 25 | `apd_base_amt` | numeric(19,8) | NO |
| 26 | `apd_base_vat` | numeric(19,8) | NO |
| 27 | `apd_ac_code` | varchar(15) | NO |
| 28 | `apd_dept` | varchar(30) | NO |
| 29 | `apd_analy1_code` | varchar(30) | NO |
| 30 | `apd_analy1_name` | varchar(255) | NO |
| 31 | `apd_analy2_code` | varchar(30) | NO |
| 32 | `apd_analy2_name` | varchar(255) | NO |
| 33 | `apd_analy3_code` | varchar(30) | NO |
| 34 | `apd_analy3_name` | varchar(255) | NO |
| 35 | `apd_analy4_code` | varchar(30) | NO |
| 36 | `apd_analy4_name` | varchar(255) | NO |
| 37 | `apd_inv_amt` | numeric(19,8) | NO |
| 38 | `apd_inv_nbr` | varchar(255) | NO |
| 39 | `apd_rmks` | varchar(255) | NO |
| 40 | `apd_crt_by` | varchar(12) | NO |
| 41 | `apd_crt_date` | datetime | NO |
| 42 | `apd_mod_times` | int(10,0) | NO |
| 43 | `apd_mod_by` | varchar(12) | NO |
| 44 | `apd_mod_date` | datetime | NO |
| 45 | `apd_char1` | varchar(255) | NO |
| 46 | `apd_char2` | varchar(255) | NO |
| 47 | `apd_char3` | varchar(255) | NO |
| 48 | `apd_char4` | varchar(255) | NO |
| 49 | `apd_char5` | varchar(255) | NO |
| 50 | `apd_char6` | varchar(255) | NO |
| 51 | `apd_qty1` | decimal(19,8) | NO |
| 52 | `apd_qty2` | decimal(19,8) | NO |
| 53 | `apd_inv_amt_un` | numeric(20,8) | YES |
| 54 | `prh_nbr` | varchar(15) | NO |
| 55 | `prh_part` | varchar(30) | NO |
| 56 | `prh_ps_nbr` | varchar(30) | NO |
| 57 | `pt_desc1` | varchar(255) | NO |
| 58 | `pt_char1` | varchar(255) | NO |
| 59 | `pt_char2` | varchar(255) | NO |
| 60 | `pt_char5` | varchar(255) | NO |
| 61 | `ap_terms` | varchar(10) | NO |
| 62 | `cm_type` | varchar(255) | NO |

### `dbo.v_apn_cert_amt` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `apn_nbr` | varchar(15) | NO |
| 2 | `apn_doc_code` | varchar(15) | NO |
| 3 | `apn_company` | varchar(8) | NO |
| 4 | `apn_date` | datetime | NO |
| 5 | `apn_vendor` | varchar(8) | NO |
| 6 | `apn_curr` | varchar(4) | NO |
| 7 | `apn_vat_rate` | numeric(19,8) | NO |
| 8 | `apn_inv_type` | varchar(1) | NO |
| 9 | `apn_inv_nbr` | varchar(255) | NO |
| 10 | `apn_vo_nbr` | varchar(15) | NO |
| 11 | `apn_rmks` | varchar(255) | NO |
| 12 | `apn_crt_by` | varchar(12) | NO |
| 13 | `apn_crt_date` | datetime | NO |
| 14 | `apn_mod_times` | int(10,0) | NO |
| 15 | `apn_mod_by` | varchar(12) | NO |
| 16 | `apn_mod_date` | datetime | NO |
| 17 | `apn_pst` | bit | NO |
| 18 | `apn_pst_by` | varchar(12) | NO |
| 19 | `apn_pst_date` | datetime | YES |
| 20 | `apn_prog_code` | varchar(12) | NO |
| 21 | `apn_char1` | varchar(255) | NO |
| 22 | `apn_char2` | varchar(255) | NO |
| 23 | `apn_char3` | varchar(255) | NO |
| 24 | `apn_char4` | varchar(255) | NO |
| 25 | `apn_char5` | varchar(255) | NO |
| 26 | `apn_char6` | varchar(255) | NO |
| 27 | `apn_qty1` | decimal(19,8) | NO |
| 28 | `apn_qty2` | decimal(19,8) | NO |
| 29 | `apn_amt_tot` | numeric(19,8) | NO |
| 30 | `apn_amt_ex` | numeric(19,8) | NO |
| 31 | `apn_amt_tax` | numeric(19,8) | NO |
| 32 | `apn_cert_amt` | numeric(19,8) | YES |
| 33 | `apn_cert_vat` | numeric(19,8) | YES |
| 34 | `ancd_cert_amt` | numeric(38,8) | NO |
| 35 | `ancd_cert_vat` | numeric(38,8) | NO |
| 36 | `open_amt` | numeric(38,8) | YES |
| 37 | `open_vat` | numeric(38,8) | YES |

### `dbo.v_apnd_pl_desc` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `账套名称` | varchar(50) | NO |
| 2 | `供应商代码` | varchar(8) | NO |
| 3 | `供应商全称` | varchar(255) | NO |
| 4 | `支付方式` | varchar(255) | NO |
| 5 | `税率%` | numeric(19,8) | NO |
| 6 | `产品组` | varchar(30) | NO |
| 7 | `本币含税金额` | numeric(38,15) | YES |
| 8 | `[本币未税金额` | numeric(38,15) | YES |
| 9 | `本币税额` | numeric(38,15) | YES |

### `dbo.v_ar_crd` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_flow_no` | int(10,0) | NO |
| 2 | `sdh_dn_dn` | varchar(15) | NO |
| 3 | `sdh_dnd_line` | int(10,0) | NO |
| 4 | `sdh_so_nbr` | varchar(15) | NO |
| 5 | `sdh_sod_line` | int(10,0) | NO |
| 6 | `sdh_part` | varchar(30) | NO |
| 7 | `sdh_qty_shp` | numeric(19,8) | NO |
| 8 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 9 | `sdh_um` | varchar(4) | NO |
| 10 | `sdh_dn_date` | datetime | NO |
| 11 | `sdh_cust` | varchar(8) | NO |
| 12 | `so_po` | varchar(255) | NO |
| 13 | `pt_desc1` | varchar(255) | NO |
| 14 | `si_company` | varchar(8) | NO |
| 15 | `sdh_site` | varchar(8) | NO |
| 16 | `sdh_dn_type` | varchar(1) | NO |
| 17 | `sdh_curr` | varchar(4) | NO |
| 18 | `sdh_sod_price` | decimal(19,8) | NO |
| 19 | `sdh_so_vat` | decimal(19,8) | NO |
| 20 | `ard_qty_pay` | numeric(38,8) | NO |

### `dbo.v_ar_dnd` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_flow_no` | int(10,0) | NO |
| 2 | `sdh_dn_dn` | varchar(15) | NO |
| 3 | `sdh_dnd_line` | int(10,0) | NO |
| 4 | `sdh_so_nbr` | varchar(15) | NO |
| 5 | `sdh_sod_line` | int(10,0) | NO |
| 6 | `sdh_part` | varchar(30) | NO |
| 7 | `sdh_qty_shp` | numeric(19,8) | NO |
| 8 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 9 | `sdh_um` | varchar(4) | NO |
| 10 | `sdh_dn_date` | datetime | NO |
| 11 | `sdh_cust` | varchar(8) | NO |
| 12 | `so_po` | varchar(255) | NO |
| 13 | `pt_desc1` | varchar(255) | NO |
| 14 | `si_company` | varchar(8) | NO |
| 15 | `sdh_site` | varchar(8) | NO |
| 16 | `sdh_dn_type` | varchar(1) | NO |
| 17 | `sdh_curr` | varchar(4) | NO |
| 18 | `sdh_sod_price` | decimal(19,8) | NO |
| 19 | `sdh_so_vat` | decimal(19,8) | NO |
| 20 | `ard_qty_pay` | numeric(38,8) | NO |

### `dbo.v_ard_det_OA` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `en_cname` | varchar(50) | NO |
| 2 | `ar_nbr` | varchar(15) | NO |
| 3 | `ar_date` | datetime | NO |
| 4 | `ar_customer` | varchar(8) | NO |
| 5 | `cm_name` | varchar(255) | NO |
| 6 | `ar_curr` | varchar(4) | NO |
| 7 | `ar_vat_rate` | numeric(19,8) | NO |
| 8 | `ar_terms` | varchar(10) | NO |
| 9 | `ard_line` | int(10,0) | NO |
| 10 | `ard_src` | varchar(1) | NO |
| 11 | `ard_src_nbr` | varchar(15) | NO |
| 12 | `ard_src_line` | int(10,0) | NO |
| 13 | `sdh_part` | varchar(30) | NO |
| 14 | `pt_desc1` | varchar(255) | NO |
| 15 | `pt_spec` | varchar(255) | NO |
| 16 | `pl_desc` | varchar(30) | NO |
| 17 | `ard_qty_pay` | numeric(19,8) | NO |
| 18 | `ard_sod_price` | decimal(19,8) | NO |
| 19 | `ard_ar_amt` | numeric(19,8) | NO |
| 20 | `ard_curr_amt` | numeric(19,8) | NO |
| 21 | `ard_curr_vat` | numeric(19,8) | NO |
| 22 | `ard_base_ar_amt` | numeric(19,8) | NO |
| 23 | `ard_base_amt` | numeric(19,8) | NO |
| 24 | `ard_base_vat` | numeric(19,8) | NO |
| 25 | `sdh_so_nbr` | varchar(15) | NO |
| 26 | `dn_addr` | varchar(255) | NO |
| 27 | `so_group` | varchar(255) | NO |
| 28 | `so_char2` | varchar(255) | NO |
| 29 | `gend_property1` | varchar(255) | NO |

### `dbo.v_ard_line` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ar_nbr` | varchar(15) | NO |
| 2 | `ar_date` | datetime | NO |
| 3 | `ar_company` | varchar(8) | NO |
| 4 | `ar_customer` | varchar(8) | NO |
| 5 | `ar_curr` | varchar(4) | NO |
| 6 | `ar_pst` | bit | NO |
| 7 | `ar_inv_amt` | numeric(19,8) | NO |
| 8 | `ar_amt` | numeric(19,8) | NO |
| 9 | `ar_paid_amt` | numeric(19,8) | NO |
| 10 | `ar_vat_rate` | numeric(19,8) | NO |
| 11 | `ard_nbr` | varchar(15) | NO |
| 12 | `ard_line` | int(10,0) | NO |
| 13 | `ard_src` | varchar(1) | NO |
| 14 | `ard_src_nbr` | varchar(15) | NO |
| 15 | `ard_src_line` | int(10,0) | NO |
| 16 | `ard_src_date` | datetime | YES |
| 17 | `ard_qty_pay` | numeric(19,8) | NO |
| 18 | `ard_src_price` | decimal(19,8) | NO |
| 19 | `ard_sod_price` | decimal(19,8) | NO |
| 20 | `ard_minus_amt` | numeric(19,8) | NO |
| 21 | `ard_ar_amt` | numeric(19,8) | NO |
| 22 | `ard_curr_amt` | numeric(19,8) | NO |
| 23 | `ard_curr_vat` | numeric(19,8) | NO |
| 24 | `ard_base_ar_amt` | numeric(19,8) | NO |
| 25 | `ard_base_amt` | numeric(19,8) | NO |
| 26 | `ard_base_vat` | numeric(19,8) | NO |
| 27 | `ard_ac_code` | varchar(15) | NO |
| 28 | `ard_dept` | varchar(30) | NO |
| 29 | `ard_analy1_code` | varchar(30) | NO |
| 30 | `ard_analy1_name` | varchar(255) | NO |
| 31 | `ard_analy2_code` | varchar(30) | NO |
| 32 | `ard_analy2_name` | varchar(255) | NO |
| 33 | `ard_analy3_code` | varchar(30) | NO |
| 34 | `ard_analy3_name` | varchar(255) | NO |
| 35 | `ard_analy4_code` | varchar(30) | NO |
| 36 | `ard_analy4_name` | varchar(255) | NO |
| 37 | `ard_rmks` | varchar(255) | NO |
| 38 | `ard_crt_by` | varchar(12) | NO |
| 39 | `ard_crt_date` | datetime | NO |
| 40 | `ard_mod_times` | int(10,0) | NO |
| 41 | `ard_mod_by` | varchar(12) | NO |
| 42 | `ard_mod_date` | datetime | NO |
| 43 | `ard_char1` | varchar(255) | NO |
| 44 | `ard_char2` | varchar(255) | NO |
| 45 | `ard_char3` | varchar(255) | NO |
| 46 | `ard_char4` | varchar(255) | NO |
| 47 | `ard_char5` | varchar(255) | NO |
| 48 | `ard_char6` | varchar(255) | NO |
| 49 | `ard_qty1` | decimal(19,8) | NO |
| 50 | `ard_qty2` | decimal(19,8) | NO |
| 51 | `ard_inv_nbr` | varchar(15) | NO |
| 52 | `ard_inv_line` | int(10,0) | NO |
| 53 | `sdh_so_nbr` | varchar(15) | NO |
| 54 | `sdh_part` | varchar(30) | NO |
| 55 | `so_po` | varchar(255) | NO |
| 56 | `pt_desc1` | varchar(255) | YES |

### `dbo.v_asid_det` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asi_nbr` | varchar(15) | NO |
| 2 | `asi_date` | datetime | NO |
| 3 | `asi_type` | varchar(1) | NO |
| 4 | `asi_cust` | varchar(8) | NO |
| 5 | `asi_act_date` | datetime | NO |
| 6 | `asi_rmks` | varchar(255) | NO |
| 7 | `asi_site` | varchar(8) | NO |
| 8 | `asi_wf_status` | varchar(1) | NO |
| 9 | `asi_prog_code` | varchar(12) | NO |
| 10 | `asi_crt_by` | varchar(12) | NO |
| 11 | `asi_crt_date` | datetime | NO |
| 12 | `asi_mod_times` | int(10,0) | NO |
| 13 | `asi_mod_by` | varchar(12) | NO |
| 14 | `asi_mod_date` | datetime | NO |
| 15 | `asi_pst` | bit | NO |
| 16 | `asi_pst_by` | varchar(12) | NO |
| 17 | `asi_pst_date` | datetime | YES |
| 18 | `asi_char1` | varchar(255) | NO |
| 19 | `asi_char2` | varchar(255) | NO |
| 20 | `asi_char3` | varchar(255) | NO |
| 21 | `asi_char4` | varchar(255) | NO |
| 22 | `asi_char5` | varchar(255) | NO |
| 23 | `asi_char6` | varchar(255) | NO |
| 24 | `asi_qty1` | decimal(19,8) | NO |
| 25 | `asi_qty2` | decimal(19,8) | NO |
| 26 | `asid_nbr` | varchar(15) | NO |
| 27 | `asid_line` | int(10,0) | NO |
| 28 | `asid_part` | varchar(30) | NO |
| 29 | `asid_qty_a` | numeric(19,8) | NO |
| 30 | `asid_qty_b` | numeric(19,8) | NO |
| 31 | `asid_qty_c` | numeric(19,8) | NO |
| 32 | `asid_req` | varchar(30) | NO |
| 33 | `asid_src_nbr` | varchar(15) | NO |
| 34 | `asid_src_line` | int(10,0) | NO |
| 35 | `asid_ast_code` | varchar(15) | NO |
| 36 | `asid_src_date` | datetime | NO |
| 37 | `asid_replace` | bit | NO |
| 38 | `asid_rmks` | varchar(255) | NO |
| 39 | `asid_crt_by` | varchar(12) | NO |
| 40 | `asid_crt_date` | datetime | NO |
| 41 | `asid_mod_times` | int(10,0) | NO |
| 42 | `asid_mod_by` | varchar(12) | NO |
| 43 | `asid_mod_date` | datetime | NO |
| 44 | `asid_char1` | varchar(255) | NO |
| 45 | `asid_char2` | varchar(255) | NO |
| 46 | `asid_char3` | varchar(255) | NO |
| 47 | `asid_char4` | varchar(255) | NO |
| 48 | `asid_char5` | varchar(255) | NO |
| 49 | `asid_char6` | varchar(255) | NO |
| 50 | `asid_qty1` | decimal(19,8) | NO |
| 51 | `asid_qty2` | decimal(19,8) | NO |
| 52 | `asid_pro_desc` | varchar(255) | NO |
| 53 | `asid_deal_way` | varchar(30) | NO |
| 54 | `asid_fee_way` | varchar(30) | NO |
| 55 | `asid_iqc_need` | varchar(1) | NO |
| 56 | `asdt_code` | varchar(30) | NO |
| 57 | `asdt_desc` | varchar(255) | NO |
| 58 | `asdt_rmks` | varchar(255) | NO |
| 59 | `asdt_start` | datetime | NO |
| 60 | `asdt_end` | datetime | NO |
| 61 | `asdt_rtn_need` | varchar(1) | NO |
| 62 | `asdt_rtn_seq` | varchar(1) | NO |
| 63 | `asdt_iqc_need` | varchar(1) | NO |
| 64 | `asdt_other_pt` | varchar(1) | NO |
| 65 | `asdt_qty_more` | varchar(1) | NO |
| 66 | `asdt_fee_ctrl` | varchar(1) | NO |
| 67 | `asdt_crt_by` | varchar(12) | NO |
| 68 | `asdt_crt_date` | datetime | NO |
| 69 | `asdt_mod_times` | int(10,0) | NO |
| 70 | `asdt_mod_by` | varchar(12) | NO |
| 71 | `asdt_mod_date` | datetime | NO |
| 72 | `asdt_pst` | bit | NO |
| 73 | `asdt_pst_by` | varchar(12) | NO |
| 74 | `asdt_pst_date` | datetime | YES |
| 75 | `asdt_char1` | varchar(255) | NO |
| 76 | `asdt_char2` | varchar(255) | NO |
| 77 | `asdt_char3` | varchar(255) | NO |
| 78 | `asdt_char4` | varchar(255) | NO |
| 79 | `asdt_char5` | varchar(255) | NO |
| 80 | `asdt_char6` | varchar(255) | NO |
| 81 | `asdt_qty1` | decimal(19,8) | NO |
| 82 | `asdt_qty2` | decimal(19,8) | NO |
| 83 | `asqd_src_nbr` | varchar(15) | YES |
| 84 | `asqd_src_line` | int(10,0) | YES |
| 85 | `asqd_qty` | numeric(38,8) | YES |
| 86 | `asqd_qty_unpst` | numeric(38,8) | YES |

### `dbo.v_asid3_det` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asid3_nbr` | varchar(15) | NO |
| 2 | `asid3_line` | int(10,0) | NO |
| 3 | `asid3_seq` | int(10,0) | NO |
| 4 | `asid3_src` | varchar(1) | NO |
| 5 | `asid3_part` | varchar(30) | NO |
| 6 | `asid3_qty` | numeric(19,8) | NO |
| 7 | `asid3_status` | varchar(1) | NO |
| 8 | `asid3_qty_out` | numeric(19,8) | NO |
| 9 | `asid3_qty_scr` | numeric(19,8) | NO |
| 10 | `asid3_rmks` | varchar(255) | NO |
| 11 | `asid3_crt_by` | varchar(12) | NO |
| 12 | `asid3_crt_date` | datetime | NO |
| 13 | `asid3_mod_times` | int(10,0) | NO |
| 14 | `asid3_mod_by` | varchar(12) | NO |
| 15 | `asid3_mod_date` | datetime | NO |
| 16 | `asid3_char1` | varchar(255) | NO |
| 17 | `asid3_char2` | varchar(255) | NO |
| 18 | `asid3_char3` | varchar(255) | NO |
| 19 | `asid3_char4` | varchar(255) | NO |
| 20 | `asid3_char5` | varchar(255) | NO |
| 21 | `asid3_char6` | varchar(255) | NO |
| 22 | `asid3_qty1` | decimal(19,8) | NO |
| 23 | `asid3_qty2` | decimal(19,8) | NO |
| 24 | `asi_nbr` | varchar(15) | NO |
| 25 | `asi_date` | datetime | NO |
| 26 | `asi_type` | varchar(1) | NO |
| 27 | `asi_cust` | varchar(8) | NO |
| 28 | `asi_act_date` | datetime | NO |
| 29 | `asi_rmks` | varchar(255) | NO |
| 30 | `asi_site` | varchar(8) | NO |
| 31 | `asi_wf_status` | varchar(1) | NO |
| 32 | `asi_prog_code` | varchar(12) | NO |
| 33 | `asi_crt_by` | varchar(12) | NO |
| 34 | `asi_crt_date` | datetime | NO |
| 35 | `asi_mod_times` | int(10,0) | NO |
| 36 | `asi_mod_by` | varchar(12) | NO |
| 37 | `asi_mod_date` | datetime | NO |
| 38 | `asi_pst` | bit | NO |
| 39 | `asi_pst_by` | varchar(12) | NO |
| 40 | `asi_pst_date` | datetime | YES |
| 41 | `asi_char1` | varchar(255) | NO |
| 42 | `asi_char2` | varchar(255) | NO |
| 43 | `asi_char3` | varchar(255) | NO |
| 44 | `asi_char4` | varchar(255) | NO |
| 45 | `asi_char5` | varchar(255) | NO |
| 46 | `asi_char6` | varchar(255) | NO |
| 47 | `asi_qty1` | decimal(19,8) | NO |
| 48 | `asi_qty2` | decimal(19,8) | NO |
| 49 | `asid_nbr` | varchar(15) | NO |
| 50 | `asid_line` | int(10,0) | NO |
| 51 | `asid_part` | varchar(30) | NO |
| 52 | `asid_qty_a` | numeric(19,8) | NO |
| 53 | `asid_qty_b` | numeric(19,8) | NO |
| 54 | `asid_qty_c` | numeric(19,8) | NO |
| 55 | `asid_req` | varchar(30) | NO |
| 56 | `asid_src_nbr` | varchar(15) | NO |
| 57 | `asid_src_line` | int(10,0) | NO |
| 58 | `asid_ast_code` | varchar(15) | NO |
| 59 | `asid_src_date` | datetime | NO |
| 60 | `asid_replace` | bit | NO |
| 61 | `asid_rmks` | varchar(255) | NO |
| 62 | `asid_crt_by` | varchar(12) | NO |
| 63 | `asid_crt_date` | datetime | NO |
| 64 | `asid_mod_times` | int(10,0) | NO |
| 65 | `asid_mod_by` | varchar(12) | NO |
| 66 | `asid_mod_date` | datetime | NO |
| 67 | `asid_char1` | varchar(255) | NO |
| 68 | `asid_char2` | varchar(255) | NO |
| 69 | `asid_char3` | varchar(255) | NO |
| 70 | `asid_char4` | varchar(255) | NO |
| 71 | `asid_char5` | varchar(255) | NO |
| 72 | `asid_char6` | varchar(255) | NO |
| 73 | `asid_qty1` | decimal(19,8) | NO |
| 74 | `asid_qty2` | decimal(19,8) | NO |
| 75 | `asid_pro_desc` | varchar(255) | NO |
| 76 | `asid_deal_way` | varchar(30) | NO |
| 77 | `asid_fee_way` | varchar(30) | NO |
| 78 | `asid_iqc_need` | varchar(1) | NO |
| 79 | `asod_src_nbr` | varchar(15) | YES |
| 80 | `asod_src_line` | int(10,0) | YES |
| 81 | `asod_src_seq` | int(10,0) | YES |
| 82 | `asod_qty` | numeric(38,8) | YES |
| 83 | `qty_left` | numeric(21,8) | YES |
| 84 | `asod_qty_unpst` | numeric(38,8) | NO |

### `dbo.v_asqd2_det` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `asqd2_nbr` | varchar(15) | NO |
| 2 | `asqd2_line` | int(10,0) | NO |
| 3 | `asqd2_part` | varchar(30) | NO |
| 4 | `asqd2_qty` | numeric(38,8) | YES |
| 5 | `asqd2_qty_iss` | numeric(38,8) | YES |
| 6 | `asqd_nbr` | varchar(15) | NO |
| 7 | `asqd_line` | int(10,0) | NO |
| 8 | `asqd_src_nbr` | varchar(15) | NO |
| 9 | `asqd_src_line` | int(10,0) | NO |
| 10 | `asqd_part` | varchar(30) | NO |
| 11 | `asqd_qty` | numeric(19,8) | NO |
| 12 | `asqd_can_fix` | bit | NO |
| 13 | `asqd_reason` | varchar(255) | NO |
| 14 | `asqd_deal_type` | varchar(1) | NO |
| 15 | `asqd_loc` | varchar(8) | NO |
| 16 | `asqd_lot` | varchar(18) | NO |
| 17 | `asqd_rmks` | varchar(255) | NO |
| 18 | `asqd_crt_by` | varchar(12) | NO |
| 19 | `asqd_crt_date` | datetime | NO |
| 20 | `asqd_mod_times` | int(10,0) | NO |
| 21 | `asqd_mod_by` | varchar(12) | NO |
| 22 | `asqd_mod_date` | datetime | NO |
| 23 | `asqd_char1` | varchar(255) | NO |
| 24 | `asqd_char2` | varchar(255) | NO |
| 25 | `asqd_char3` | varchar(255) | NO |
| 26 | `asqd_char4` | varchar(255) | NO |
| 27 | `asqd_char5` | varchar(255) | NO |
| 28 | `asqd_char6` | varchar(255) | NO |
| 29 | `asqd_qty1` | decimal(19,8) | NO |
| 30 | `asqd_qty2` | decimal(19,8) | NO |
| 31 | `asqd_need_fix` | bit | NO |
| 32 | `asq_nbr` | varchar(15) | NO |
| 33 | `asq_date` | datetime | NO |
| 34 | `asq_rmks` | varchar(255) | NO |
| 35 | `asq_site` | varchar(8) | NO |
| 36 | `asq_wf_status` | varchar(1) | NO |
| 37 | `asq_prog_code` | varchar(12) | NO |
| 38 | `asq_crt_by` | varchar(12) | NO |
| 39 | `asq_crt_date` | datetime | NO |
| 40 | `asq_mod_times` | int(10,0) | NO |
| 41 | `asq_mod_by` | varchar(12) | NO |
| 42 | `asq_mod_date` | datetime | NO |
| 43 | `asq_pst` | bit | NO |
| 44 | `asq_pst_by` | varchar(12) | NO |
| 45 | `asq_pst_date` | datetime | YES |
| 46 | `asq_chk` | bit | NO |
| 47 | `asq_chk_by` | varchar(12) | NO |
| 48 | `asq_chk_date` | datetime | YES |
| 49 | `asq_char1` | varchar(255) | NO |
| 50 | `asq_char2` | varchar(255) | NO |
| 51 | `asq_char3` | varchar(255) | NO |
| 52 | `asq_char4` | varchar(255) | NO |
| 53 | `asq_char5` | varchar(255) | NO |
| 54 | `asq_char6` | varchar(255) | NO |
| 55 | `asq_qty1` | decimal(19,8) | NO |
| 56 | `asq_qty2` | decimal(19,8) | NO |
| 57 | `asid_nbr` | varchar(15) | NO |
| 58 | `asid_line` | int(10,0) | NO |
| 59 | `asid_part` | varchar(30) | NO |
| 60 | `asid_qty_a` | numeric(19,8) | NO |
| 61 | `asid_qty_b` | numeric(19,8) | NO |
| 62 | `asid_qty_c` | numeric(19,8) | NO |
| 63 | `asid_req` | varchar(30) | NO |
| 64 | `asid_src_nbr` | varchar(15) | NO |
| 65 | `asid_src_line` | int(10,0) | NO |
| 66 | `asid_ast_code` | varchar(15) | NO |
| 67 | `asid_src_date` | datetime | NO |
| 68 | `asid_replace` | bit | NO |
| 69 | `asid_rmks` | varchar(255) | NO |
| 70 | `asid_crt_by` | varchar(12) | NO |
| 71 | `asid_crt_date` | datetime | NO |
| 72 | `asid_mod_times` | int(10,0) | NO |
| 73 | `asid_mod_by` | varchar(12) | NO |
| 74 | `asid_mod_date` | datetime | NO |
| 75 | `asid_char1` | varchar(255) | NO |
| 76 | `asid_char2` | varchar(255) | NO |
| 77 | `asid_char3` | varchar(255) | NO |
| 78 | `asid_char4` | varchar(255) | NO |
| 79 | `asid_char5` | varchar(255) | NO |
| 80 | `asid_char6` | varchar(255) | NO |
| 81 | `asid_qty1` | decimal(19,8) | NO |
| 82 | `asid_qty2` | decimal(19,8) | NO |
| 83 | `asid_pro_desc` | varchar(255) | NO |
| 84 | `asid_deal_way` | varchar(30) | NO |
| 85 | `asid_fee_way` | varchar(30) | NO |
| 86 | `asid_iqc_need` | varchar(1) | NO |
| 87 | `acgd2_qty` | numeric(38,8) | NO |

### `dbo.v_cp_part` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cp_part` | varchar(30) | NO |
| 2 | `cp_cust_part` | varchar(80) | NO |

### `dbo.v_cp_part_all` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `cp_part` | varchar(30) | NO |
| 2 | `cp_cust_part` | varchar(80) | NO |
| 3 | `tmp_seq` | bigint(19,0) | YES |

### `dbo.v_hremp_mstr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `hremp_code` | varchar(15) | NO |
| 2 | `hremp_cname` | varchar(50) | NO |
| 3 | `hremp_ename` | varchar(50) | NO |
| 4 | `hremp_aid_code` | varchar(10) | NO |
| 5 | `hremp_dept` | varchar(10) | NO |
| 6 | `hremp_dept2` | varchar(30) | NO |
| 7 | `hremp_position` | varchar(15) | NO |
| 8 | `hremp_trades` | varchar(30) | NO |
| 9 | `hremp_id_type` | varchar(30) | NO |
| 10 | `hremp_id_num` | varchar(30) | NO |
| 11 | `hremp_id_valid` | datetime | NO |
| 12 | `hremp_id_by` | varchar(80) | NO |
| 13 | `hremp_birthday` | datetime | NO |
| 14 | `hremp_gender` | varchar(1) | NO |
| 15 | `hremp_nation` | varchar(30) | NO |
| 16 | `hremp_hometown` | varchar(30) | NO |
| 17 | `hremp_relegion` | varchar(30) | NO |
| 18 | `hremp_marital` | varchar(1) | NO |
| 19 | `hremp_diploma` | varchar(30) | NO |
| 20 | `hremp_school` | varchar(50) | NO |
| 21 | `hremp_major` | varchar(30) | NO |
| 22 | `hremp_grd_date` | datetime | YES |
| 23 | `hremp_prof` | varchar(30) | NO |
| 24 | `hremp_prof_date` | datetime | YES |
| 25 | `hremp_fore_lang` | varchar(30) | NO |
| 26 | `hremp_fore_lvl` | varchar(30) | NO |
| 27 | `hremp_tele` | varchar(50) | NO |
| 28 | `hremp_email` | varchar(80) | NO |
| 29 | `hremp_oth_con` | varchar(80) | NO |
| 30 | `hremp_labor_num` | varchar(50) | NO |
| 31 | `hremp_enter_date` | datetime | NO |
| 32 | `hremp_cont_from` | datetime | YES |
| 33 | `hremp_cont_to` | datetime | YES |
| 34 | `hremp_cont_type` | varchar(30) | NO |
| 35 | `hremp_trail_from` | datetime | YES |
| 36 | `hremp_trail_to` | datetime | YES |
| 37 | `hremp_offi_date` | datetime | YES |
| 38 | `hremp_source` | varchar(30) | NO |
| 39 | `hremp_intr_by` | varchar(30) | NO |
| 40 | `hremp_deposit` | numeric(19,8) | NO |
| 41 | `hremp_status` | varchar(1) | NO |
| 42 | `hremp_leave_date` | datetime | YES |
| 43 | `hremp_leave_rsn` | varchar(30) | NO |
| 44 | `hremp_home_add` | varchar(255) | NO |
| 45 | `hremp_home_zip` | varchar(10) | NO |
| 46 | `hremp_home_cont` | varchar(30) | NO |
| 47 | `hremp_home_tele` | varchar(50) | NO |
| 48 | `hremp_curr_add` | varchar(255) | NO |
| 49 | `hremp_curr_zip` | varchar(10) | NO |
| 50 | `hremp_emgn_cont` | varchar(30) | NO |
| 51 | `hremp_emgn_tele` | varchar(50) | NO |
| 52 | `hremp_dorm_num` | varchar(10) | NO |
| 53 | `hremp_sly_level` | varchar(10) | NO |
| 54 | `hremp_sly_rmks` | varchar(255) | NO |
| 55 | `hremp_pension` | varchar(30) | NO |
| 56 | `hremp_medical` | varchar(30) | NO |
| 57 | `hremp_unemploy` | varchar(30) | NO |
| 58 | `hremp_provident` | varchar(30) | NO |
| 59 | `hremp_bank_acc1` | varchar(30) | NO |
| 60 | `hremp_bank_acc2` | varchar(30) | NO |
| 61 | `hremp_rule` | varchar(10) | NO |
| 62 | `hremp_need_card` | bit | NO |
| 63 | `hremp_card_id` | varchar(50) | NO |
| 64 | `hremp_card_date` | datetime | YES |
| 65 | `hremp_sch` | varchar(15) | NO |
| 66 | `hremp_photo` | image(2147483647) | YES |
| 67 | `hremp_rmks` | varchar(255) | NO |
| 68 | `hremp_crt_by` | varchar(12) | NO |
| 69 | `hremp_crt_date` | datetime | NO |
| 70 | `hremp_mod_times` | int(10,0) | NO |
| 71 | `hremp_mod_by` | varchar(12) | NO |
| 72 | `hremp_mod_date` | datetime | NO |
| 73 | `hremp_pst` | bit | NO |
| 74 | `hremp_pst_by` | varchar(12) | NO |
| 75 | `hremp_pst_date` | datetime | YES |
| 76 | `hremp_char1` | varchar(255) | NO |
| 77 | `hremp_char2` | varchar(255) | NO |
| 78 | `hremp_char3` | varchar(255) | NO |
| 79 | `hremp_char4` | varchar(255) | NO |
| 80 | `hremp_char5` | varchar(255) | NO |
| 81 | `hremp_char6` | varchar(255) | NO |
| 82 | `hremp_char7` | varchar(255) | NO |
| 83 | `hremp_char8` | varchar(255) | NO |
| 84 | `hremp_char9` | varchar(255) | NO |
| 85 | `hremp_qty1` | decimal(19,8) | NO |
| 86 | `hremp_qty2` | decimal(19,8) | NO |
| 87 | `hremp_qty3` | decimal(19,8) | NO |
| 88 | `hremp_qty4` | decimal(19,8) | NO |
| 89 | `hremp_qty5` | decimal(19,8) | NO |
| 90 | `hremp_qty6` | decimal(19,8) | NO |
| 91 | `dp_name` | varchar(50) | YES |
| 92 | `hrpo_name` | varchar(50) | YES |
| 93 | `dept2_name` | varchar(255) | YES |
| 94 | `trades_name` | varchar(255) | YES |

### `dbo.v_import_code` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `t_type` | varchar(1) | NO |
| 2 | `pt_part` | varchar(30) | NO |
| 3 | `pt_desc1` | varchar(255) | NO |

### `dbo.v_inv_mstr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `inv_nbr` | varchar(15) | NO |
| 2 | `inv_cust` | varchar(8) | NO |
| 3 | `inv_eff_date` | datetime | NO |
| 4 | `inv_due_date` | datetime | NO |
| 5 | `inv_disc_date` | datetime | NO |
| 6 | `inv_cr_terms` | varchar(10) | NO |
| 7 | `inv_disc` | decimal(19,8) | NO |
| 8 | `inv_vat` | decimal(19,8) | NO |
| 9 | `inv_curr` | varchar(4) | NO |
| 10 | `inv_rmks` | varchar(255) | NO |
| 11 | `inv_site` | varchar(8) | NO |
| 12 | `inv_prog_code` | varchar(12) | NO |
| 13 | `inv_crt_by` | varchar(12) | NO |
| 14 | `inv_crt_date` | datetime | NO |
| 15 | `inv_mod_times` | int(10,0) | NO |
| 16 | `inv_mod_by` | varchar(12) | NO |
| 17 | `inv_mod_date` | datetime | NO |
| 18 | `inv_pst` | bit | NO |
| 19 | `inv_pst_by` | varchar(12) | NO |
| 20 | `inv_pst_date` | datetime | YES |
| 21 | `inv_char1` | varchar(255) | NO |
| 22 | `inv_char2` | varchar(255) | NO |
| 23 | `inv_char3` | varchar(255) | NO |
| 24 | `inv_char4` | varchar(255) | NO |
| 25 | `inv_char5` | varchar(255) | NO |
| 26 | `inv_char6` | varchar(255) | NO |
| 27 | `inv_qty1` | decimal(19,8) | NO |
| 28 | `inv_qty2` | decimal(19,8) | NO |
| 29 | `inv_qty_tot` | numeric(19,8) | NO |
| 30 | `inv_amt_tot` | numeric(19,8) | NO |
| 31 | `inv_amt_ex` | numeric(19,8) | NO |
| 32 | `inv_amt_tax` | numeric(19,8) | NO |
| 33 | `inv_vo_nbr` | varchar(15) | NO |
| 34 | `inv_crt_name` | varchar(30) | NO |
| 35 | `inv_mod_name` | varchar(30) | NO |
| 36 | `inv_pst_name` | varchar(30) | NO |
| 37 | `invd_amt` | numeric(38,15) | YES |

### `dbo.v_loc_inb_type` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `gend_option` | varchar(30) | YES |
| 2 | `gend_name` | varchar(255) | NO |
| 3 | `sub_type` | varchar(8) | NO |
| 4 | `sub_type_name` | varchar(255) | YES |
| 5 | `gend_property1` | varchar(255) | NO |

### `dbo.v_loc_mstr_type` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `loc_site` | varchar(8) | NO |
| 2 | `loc_loc` | varchar(8) | NO |
| 3 | `loc_desc` | varchar(30) | NO |
| 4 | `loc_type` | varchar(8) | NO |
| 5 | `loc_type_name` | varchar(255) | YES |
| 6 | `loc_cost_type` | varchar(255) | YES |

### `dbo.v_loc_type` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tp_code` | varchar(30) | YES |
| 2 | `tp_name` | varchar(255) | NO |
| 3 | `tp_auto_select` | varchar(255) | NO |

### `dbo.v_mov_cat` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `gend_gen` | varchar(30) | NO |
| 2 | `gend_option` | varchar(30) | NO |
| 3 | `gend_name` | varchar(255) | NO |
| 4 | `gend_property1` | varchar(255) | NO |
| 5 | `gend_property2` | varchar(255) | NO |
| 6 | `gend_property3` | varchar(255) | NO |
| 7 | `gend_property4` | varchar(255) | NO |
| 8 | `gend_disabled` | bit | NO |
| 9 | `gend_crt_by` | varchar(12) | NO |
| 10 | `gend_crt_date` | datetime | NO |
| 11 | `gend_char1` | varchar(255) | NO |
| 12 | `gend_char2` | varchar(255) | NO |
| 13 | `gend_char3` | varchar(255) | NO |
| 14 | `gend_char4` | varchar(255) | NO |
| 15 | `gend_char5` | varchar(255) | NO |
| 16 | `gend_char6` | varchar(255) | NO |
| 17 | `gend_qty1` | decimal(19,8) | NO |
| 18 | `gend_qty2` | decimal(19,8) | NO |
| 19 | `gend_property5` | varchar(255) | NO |
| 20 | `gend_property6` | varchar(255) | NO |
| 21 | `gend_property7` | varchar(255) | NO |
| 22 | `gend_property8` | varchar(255) | NO |
| 23 | `gend_property9` | varchar(255) | NO |
| 24 | `gend_property10` | numeric(19,8) | NO |
| 25 | `gend_property11` | numeric(19,8) | NO |
| 26 | `gend_property12` | numeric(19,8) | NO |
| 27 | `gend_property13` | numeric(19,8) | NO |
| 28 | `gend_property14` | numeric(19,8) | NO |
| 29 | `gend_property15` | numeric(19,8) | NO |
| 30 | `gend_property16` | datetime | YES |
| 31 | `gend_property17` | datetime | YES |

### `dbo.v_pc_all_price` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pc_vend` | varchar(8) | NO |
| 2 | `pc_part` | varchar(30) | NO |
| 3 | `pc_curr` | varchar(4) | NO |
| 4 | `pc_start` | datetime | NO |
| 5 | `pc_expire` | datetime | NO |
| 6 | `pc_vat` | decimal(19,8) | NO |
| 7 | `pc_qty` | numeric(19,8) | NO |
| 8 | `pc_price` | decimal(19,8) | NO |

### `dbo.v_pc_mstr_price` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pc_vend` | varchar(8) | NO |
| 2 | `pc_part` | varchar(30) | NO |
| 3 | `pc_curr` | varchar(4) | NO |
| 4 | `pc_start` | datetime | NO |
| 5 | `pc_expire` | datetime | NO |
| 6 | `pc_vat` | decimal(19,8) | NO |
| 7 | `pc_price` | decimal(19,8) | NO |

### `dbo.v_pkd_det_V` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pk_pk` | varchar(15) | NO |
| 2 | `pk_date` | datetime | NO |
| 3 | `pk_type` | varchar(1) | NO |
| 4 | `pk_wonbr` | varchar(15) | NO |
| 5 | `pk_wolot` | varchar(18) | NO |
| 6 | `pk_rmks` | varchar(255) | NO |
| 7 | `pk_wf_status` | varchar(1) | NO |
| 8 | `pk_site` | varchar(8) | NO |
| 9 | `pk_prog_code` | varchar(12) | NO |
| 10 | `pk_doc_code` | varchar(12) | NO |
| 11 | `pk_crt_by` | varchar(12) | NO |
| 12 | `pk_crt_date` | datetime | NO |
| 13 | `pk_mod_times` | int(10,0) | NO |
| 14 | `pk_mod_by` | varchar(12) | NO |
| 15 | `pk_mod_date` | datetime | NO |
| 16 | `pk_pst` | bit | NO |
| 17 | `pk_pst_by` | varchar(12) | NO |
| 18 | `pk_pst_date` | datetime | YES |
| 19 | `pk_char1` | varchar(255) | NO |
| 20 | `pk_char2` | varchar(255) | NO |
| 21 | `pk_char3` | varchar(255) | NO |
| 22 | `pk_char4` | varchar(255) | NO |
| 23 | `pk_char5` | varchar(255) | NO |
| 24 | `pk_char6` | varchar(255) | NO |
| 25 | `pk_qty1` | decimal(19,8) | NO |
| 26 | `pk_qty2` | decimal(19,8) | NO |
| 27 | `pk_src` | varchar(2) | NO |
| 28 | `pk_src_nbr` | varchar(15) | NO |
| 29 | `pk_chk` | bit | NO |
| 30 | `pk_chk_by` | varchar(12) | NO |
| 31 | `pk_chk_date` | datetime | YES |
| 32 | `pk_data_src` | varchar(1) | NO |
| 33 | `pk_data_id` | varchar(255) | NO |
| 34 | `pkd_pk` | varchar(15) | NO |
| 35 | `pkd_line` | int(10,0) | NO |
| 36 | `pkd_wo_nbr` | varchar(15) | NO |
| 37 | `pkd_wo_lot` | varchar(18) | NO |
| 38 | `pkd_seq` | int(10,0) | NO |
| 39 | `pkd_type` | varchar(8) | NO |
| 40 | `pkd_part` | varchar(30) | NO |
| 41 | `pkd_qty_req` | numeric(19,8) | NO |
| 42 | `pkd_qty_iss` | numeric(19,8) | NO |
| 43 | `pkd_site` | varchar(8) | NO |
| 44 | `pkd_loc` | varchar(8) | NO |
| 45 | `pkd_lot` | varchar(18) | NO |
| 46 | `pkd_alt` | bit | NO |
| 47 | `pkd_qty_pts_m` | numeric(19,8) | NO |
| 48 | `pkd_qty_pts_d` | numeric(19,8) | NO |
| 49 | `pkd_op` | int(10,0) | NO |
| 50 | `pkd_seq2` | int(10,0) | NO |
| 51 | `pkd_rmks` | varchar(255) | NO |
| 52 | `pkd_crt_by` | varchar(12) | NO |
| 53 | `pkd_crt_date` | datetime | NO |
| 54 | `pkd_mod_times` | int(10,0) | NO |
| 55 | `pkd_mod_by` | varchar(12) | NO |
| 56 | `pkd_mod_date` | datetime | NO |
| 57 | `pkd_char1` | varchar(255) | NO |
| 58 | `pkd_char2` | varchar(255) | NO |
| 59 | `pkd_char3` | varchar(255) | NO |
| 60 | `pkd_char4` | varchar(255) | NO |
| 61 | `pkd_char5` | varchar(255) | NO |
| 62 | `pkd_char6` | varchar(255) | NO |
| 63 | `pkd_qty1` | decimal(19,8) | NO |
| 64 | `pkd_qty2` | decimal(19,8) | NO |
| 65 | `pkd_qty_off` | numeric(19,8) | NO |
| 66 | `pkd_qty_plan` | numeric(19,8) | NO |
| 67 | `pkd_src_nbr` | varchar(15) | NO |
| 68 | `pkd_src_line` | int(10,0) | NO |
| 69 | `pkd_data_src` | varchar(1) | NO |
| 70 | `pkd_data_id` | varchar(255) | NO |
| 71 | `wo_type` | varchar(1) | NO |
| 72 | `wo_type2` | varchar(1) | NO |
| 73 | `wo_line` | varchar(8) | NO |
| 74 | `wo_part` | varchar(30) | NO |

### `dbo.v_pl_mstr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pl_prod_line` | varchar(4) | NO |
| 2 | `pl_desc` | varchar(30) | NO |
| 3 | `pl_upper` | varchar(15) | NO |
| 4 | `pl_upper_desc` | varchar(30) | NO |

### `dbo.v_pma_bank` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pma_vend` | varchar(30) | NO |
| 2 | `pma_bank` | varchar(255) | NO |
| 3 | `pma_account` | varchar(255) | NO |
| 4 | `pma_curr` | varchar(4) | NO |

### `dbo.v_po_dept` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `dp_code` | varchar(10) | NO |
| 2 | `dp_name` | varchar(50) | NO |
| 3 | `dp_manager` | varchar(30) | NO |
| 4 | `dp_rmks` | varchar(255) | NO |
| 5 | `dp_upper_dept` | varchar(10) | NO |
| 6 | `dp_crt_by` | varchar(12) | NO |
| 7 | `dp_crt_date` | datetime | NO |
| 8 | `dp_char1` | varchar(255) | NO |
| 9 | `dp_char2` | varchar(255) | NO |
| 10 | `dp_char3` | varchar(255) | NO |
| 11 | `dp_char4` | varchar(255) | NO |
| 12 | `dp_char5` | varchar(255) | NO |
| 13 | `dp_char6` | varchar(255) | NO |
| 14 | `dp_qty1` | decimal(19,8) | NO |
| 15 | `dp_qty2` | decimal(19,8) | NO |

### `dbo.v_pod_pt_desc` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `po_ord_date` | datetime | NO |
| 2 | `pod_part` | varchar(30) | NO |
| 3 | `pod_pt_desc` | varchar(255) | NO |
| 4 | `po_vend` | varchar(8) | NO |
| 5 | `vd_sort` | varchar(50) | NO |
| 6 | `pod_um` | varchar(4) | NO |
| 7 | `pod_pur_cost` | decimal(19,8) | NO |

### `dbo.v_pod_req_so` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pod_nbr` | varchar(15) | NO |
| 2 | `pod_line` | int(10,0) | NO |
| 3 | `req_pr_nbr` | varchar(15) | YES |
| 4 | `req_line` | int(10,0) | YES |
| 5 | `req_part` | varchar(30) | YES |
| 6 | `so_po` | varchar(255) | NO |
| 7 | `so_cust` | varchar(8) | NO |
| 8 | `sod_nbr` | varchar(15) | NO |
| 9 | `sod_line` | int(10,0) | NO |
| 10 | `sod_cust_part` | varchar(80) | NO |
| 11 | `cp_cust_desc` | varchar(255) | NO |
| 12 | `cp_char1` | varchar(255) | NO |
| 13 | `cp_char2` | varchar(255) | NO |

### `dbo.v_pod_sod_cust_part` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pod_nbr` | varchar(15) | NO |
| 2 | `pod_line` | int(10,0) | NO |
| 3 | `sod_nbr` | varchar(15) | NO |
| 4 | `sod_line` | int(10,0) | NO |
| 5 | `sod_cust_part` | varchar(80) | NO |
| 6 | `cp_cust_desc` | varchar(255) | NO |
| 7 | `cp_char1` | varchar(255) | NO |
| 8 | `cp_char2` | varchar(255) | NO |
| 9 | `tmp_seq` | bigint(19,0) | YES |

### `dbo.v_prh_hist` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prh_receiver` | varchar(15) | NO |
| 2 | `prh_grnd_line` | int(10,0) | NO |
| 3 | `prh_nbr` | varchar(15) | NO |
| 4 | `prh_line` | int(10,0) | NO |
| 5 | `prh_part` | varchar(30) | NO |
| 6 | `prh_qty_rcvd` | numeric(19,8) | NO |
| 7 | `prh_qty_spare_rcvd` | numeric(19,8) | NO |
| 8 | `prh_um` | varchar(4) | NO |
| 9 | `prh_rcp_date` | datetime | NO |
| 10 | `prh_vend` | varchar(8) | NO |
| 11 | `prh_ps_nbr` | varchar(30) | NO |
| 12 | `pt_desc1` | varchar(255) | NO |
| 13 | `si_company` | varchar(8) | NO |
| 14 | `prh_site` | varchar(8) | NO |
| 15 | `prh_rcp_type` | varchar(1) | NO |
| 16 | `prh_curr` | varchar(4) | NO |
| 17 | `prh_pur_cost` | decimal(19,8) | NO |
| 18 | `prh_vat` | decimal(19,8) | NO |

### `dbo.v_prh_receiver` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `prh_receiver` | varchar(15) | NO |
| 2 | `prh_rcp_date` | datetime | NO |
| 3 | `prh_vend` | varchar(8) | NO |
| 4 | `prh_rcp_type` | varchar(1) | NO |
| 5 | `prh_ps_nbr` | varchar(30) | NO |

### `dbo.v_print_hist` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `print_prog` | varchar(12) | NO |
| 2 | `print_nbr` | varchar(30) | NO |
| 3 | `print_lot` | varchar(30) | NO |
| 4 | `print_sum` | int(10,0) | YES |

### `dbo.v_ps_R` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `ps_par` | varchar(30) | NO |
| 2 | `ps_comp` | varchar(30) | NO |
| 3 | `ps_start` | datetime | NO |
| 4 | `ps_end` | datetime | NO |
| 5 | `ps_qty_m` | numeric(19,8) | NO |
| 6 | `ps_qty_d` | numeric(19,8) | NO |
| 7 | `ps_op` | int(10,0) | NO |
| 8 | `ps_scrp_pct` | decimal(19,8) | NO |
| 9 | `ps_lt_off` | int(10,0) | NO |
| 10 | `ps_seq` | int(10,0) | NO |
| 11 | `ps_rmks` | varchar(255) | NO |
| 12 | `ps_end_ecn` | varchar(15) | NO |
| 13 | `ps_crt_by` | varchar(12) | NO |
| 14 | `ps_crt_date` | datetime | NO |
| 15 | `ps_mod_times` | int(10,0) | NO |
| 16 | `ps_mod_by` | varchar(12) | NO |
| 17 | `ps_mod_date` | datetime | NO |
| 18 | `ps_char1` | varchar(255) | NO |
| 19 | `ps_char2` | varchar(255) | NO |
| 20 | `ps_char3` | varchar(255) | NO |
| 21 | `ps_char4` | varchar(255) | NO |
| 22 | `ps_char5` | varchar(255) | NO |
| 23 | `ps_char6` | varchar(255) | NO |
| 24 | `ps_qty1` | decimal(19,8) | NO |
| 25 | `ps_qty2` | decimal(19,8) | NO |
| 26 | `ps_version` | varchar(10) | NO |
| 27 | `ps_desc` | varchar(255) | NO |
| 28 | `ps_spec` | varchar(255) | NO |
| 29 | `ps_um_eng` | varchar(4) | NO |
| 30 | `ps_vend` | varchar(8) | NO |
| 31 | `ps_curr` | varchar(4) | NO |
| 32 | `ps_vat` | decimal(19,8) | NO |
| 33 | `ps_pc_nbr` | varchar(15) | NO |
| 34 | `ps_pur_cost` | decimal(19,8) | NO |
| 35 | `ps_ord_min` | numeric(19,8) | NO |
| 36 | `ps_ord_mult` | numeric(19,8) | NO |
| 37 | `ps_mod_cost` | decimal(19,8) | NO |
| 38 | `ps_oth_cost` | decimal(19,8) | NO |

### `dbo.V_pt_group` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `gend_gen` | varchar(30) | NO |
| 2 | `gend_option` | varchar(30) | NO |
| 3 | `gend_name` | varchar(255) | NO |
| 4 | `gend_property1` | varchar(255) | NO |
| 5 | `gend_property2` | varchar(255) | NO |
| 6 | `gend_property3` | varchar(255) | NO |
| 7 | `gend_property4` | varchar(255) | NO |
| 8 | `gend_disabled` | bit | NO |
| 9 | `gend_crt_by` | varchar(12) | NO |
| 10 | `gend_crt_date` | datetime | NO |
| 11 | `gend_char1` | varchar(255) | NO |
| 12 | `gend_char2` | varchar(255) | NO |
| 13 | `gend_char3` | varchar(255) | NO |
| 14 | `gend_char4` | varchar(255) | NO |
| 15 | `gend_char5` | varchar(255) | NO |
| 16 | `gend_char6` | varchar(255) | NO |
| 17 | `gend_qty1` | decimal(19,8) | NO |
| 18 | `gend_qty2` | decimal(19,8) | NO |

### `dbo.v_pt_mstr1` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pt_part` | varchar(30) | NO |
| 2 | `pt_desc1` | varchar(255) | NO |
| 3 | `pt_desc2` | varchar(255) | NO |
| 4 | `pt_custom_code` | varchar(50) | NO |
| 5 | `pt_barcode` | varchar(80) | NO |
| 6 | `pt_spec` | varchar(255) | NO |
| 7 | `pt_um` | varchar(4) | NO |
| 8 | `pt_prod_line` | varchar(4) | NO |
| 9 | `pt_added` | datetime | NO |
| 10 | `pt_part_type` | varchar(30) | NO |
| 11 | `pt_group` | varchar(30) | NO |
| 12 | `pt_draw` | varchar(18) | NO |
| 13 | `pt_picture` | varchar(255) | NO |
| 14 | `pt_rev` | varchar(4) | NO |
| 15 | `pt_status` | bit | NO |
| 16 | `pt_gross_weight` | numeric(19,8) | NO |
| 17 | `pt_net_weight` | numeric(19,8) | NO |
| 18 | `pt_case_qty` | numeric(19,8) | NO |
| 19 | `pt_scrp_pct` | decimal(19,8) | NO |
| 20 | `pt_ship_mark` | varchar(255) | NO |
| 21 | `pt_carton_l` | numeric(19,8) | NO |
| 22 | `pt_carton_w` | numeric(19,8) | NO |
| 23 | `pt_carton_h` | numeric(19,8) | NO |
| 24 | `pt_total` | numeric(19,8) | NO |
| 25 | `pt_um_eng` | varchar(4) | NO |
| 26 | `pt_um_eng_m` | decimal(19,8) | NO |
| 27 | `pt_um_eng_d` | decimal(19,8) | NO |
| 28 | `pt_um_pur` | varchar(4) | NO |
| 29 | `pt_um_pur_m` | decimal(19,8) | NO |
| 30 | `pt_um_pur_d` | decimal(19,8) | NO |
| 31 | `pt_um_sl` | varchar(4) | NO |
| 32 | `pt_um_sl_m` | decimal(19,8) | NO |
| 33 | `pt_um_sl_d` | decimal(19,8) | NO |
| 34 | `pt_um_isu` | varchar(4) | NO |
| 35 | `pt_um_isu_m` | decimal(19,8) | NO |
| 36 | `pt_um_isu_d` | decimal(19,8) | NO |
| 37 | `pt_abc` | varchar(1) | NO |
| 38 | `pt_loc` | varchar(8) | NO |
| 39 | `pt_cyc_int` | int(10,0) | NO |
| 40 | `pt_lot_serial` | bit | NO |
| 41 | `pt_lot_grp` | varchar(15) | NO |
| 42 | `pt_keeper` | varchar(12) | NO |
| 43 | `pt_shelf_life` | int(10,0) | NO |
| 44 | `pt_wo_line` | varchar(8) | NO |
| 45 | `pt_plan_ord` | bit | NO |
| 46 | `pt_time_fence` | int(10,0) | NO |
| 47 | `pt_ord_pol` | varchar(4) | NO |
| 48 | `pt_ord_qty` | numeric(19,8) | NO |
| 49 | `pt_ord_per` | int(10,0) | NO |
| 50 | `pt_sfty_stk` | numeric(19,8) | NO |
| 51 | `pt_rop` | numeric(19,8) | NO |
| 52 | `pt_buyer` | varchar(12) | NO |
| 53 | `pt_planner` | varchar(12) | NO |
| 54 | `pt_memo_item` | bit | NO |
| 55 | `pt_max_qty` | numeric(19,8) | NO |
| 56 | `pt_vend` | varchar(8) | NO |
| 57 | `pt_pm_code` | varchar(1) | NO |
| 58 | `pt_mfg_lt` | int(10,0) | NO |
| 59 | `pt_pur_lt` | int(10,0) | NO |
| 60 | `pt_insp_rqd` | bit | NO |
| 61 | `pt_gr_lt` | int(10,0) | NO |
| 62 | `pt_phantom` | bit | NO |
| 63 | `pt_ord_min` | numeric(19,8) | NO |
| 64 | `pt_ord_mult` | numeric(19,8) | NO |
| 65 | `pt_iss_batch` | numeric(19,8) | NO |
| 66 | `pt_roll_iss` | bit | NO |
| 67 | `pt_fgov_per` | decimal(19,8) | NO |
| 68 | `pt_iss_unlimit` | bit | NO |
| 69 | `pt_level` | int(10,0) | NO |
| 70 | `pt_wf_status` | varchar(1) | NO |
| 71 | `pt_crt_by` | varchar(12) | NO |
| 72 | `pt_crt_date` | datetime | NO |
| 73 | `pt_mod_times` | int(10,0) | NO |
| 74 | `pt_mod_by` | varchar(12) | NO |
| 75 | `pt_mod_date` | datetime | NO |
| 76 | `pt_pst` | bit | NO |
| 77 | `pt_pst_by` | varchar(12) | NO |
| 78 | `pt_pst_date` | datetime | YES |
| 79 | `pt_char1` | varchar(255) | NO |
| 80 | `pt_char2` | varchar(255) | NO |
| 81 | `pt_char3` | varchar(255) | NO |
| 82 | `pt_char4` | varchar(255) | NO |
| 83 | `pt_char5` | varchar(255) | NO |
| 84 | `pt_char6` | varchar(255) | NO |
| 85 | `pt_char7` | varchar(255) | NO |
| 86 | `pt_char8` | varchar(255) | NO |
| 87 | `pt_qty1` | decimal(19,8) | NO |
| 88 | `pt_qty2` | decimal(19,8) | NO |
| 89 | `pt_qty3` | decimal(19,8) | NO |
| 90 | `pt_qty4` | decimal(19,8) | NO |
| 91 | `pt_expu_perm` | bit | NO |
| 92 | `pt_exsl_perm` | bit | NO |
| 93 | `pt_loc_pos` | varchar(18) | NO |
| 94 | `pt_eng` | varchar(12) | NO |
| 95 | `pt_custom_name` | varchar(255) | NO |
| 96 | `pt_op` | int(10,0) | NO |
| 97 | `pt_backflush` | varchar(1) | NO |
| 98 | `pt_backflush_s` | varchar(1) | NO |
| 99 | `pt_sch_type` | varchar(30) | NO |
| 100 | `pt_ovr_unmrp` | bit | NO |

### `dbo.v_pt_mstr2` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pt_part` | varchar(30) | NO |
| 2 | `pt_desc1` | varchar(255) | NO |
| 3 | `pt_desc2` | varchar(255) | NO |
| 4 | `pt_custom_code` | varchar(50) | NO |
| 5 | `pt_barcode` | varchar(80) | NO |
| 6 | `pt_spec` | varchar(255) | NO |
| 7 | `pt_um` | varchar(4) | NO |
| 8 | `pt_prod_line` | varchar(4) | NO |
| 9 | `pt_added` | datetime | NO |
| 10 | `pt_part_type` | varchar(30) | NO |
| 11 | `pt_group` | varchar(30) | NO |
| 12 | `pt_draw` | varchar(18) | NO |
| 13 | `pt_picture` | varchar(255) | NO |
| 14 | `pt_rev` | varchar(4) | NO |
| 15 | `pt_status` | bit | NO |
| 16 | `pt_gross_weight` | numeric(19,8) | NO |
| 17 | `pt_net_weight` | numeric(19,8) | NO |
| 18 | `pt_case_qty` | numeric(19,8) | NO |
| 19 | `pt_scrp_pct` | decimal(19,8) | NO |
| 20 | `pt_ship_mark` | varchar(255) | NO |
| 21 | `pt_carton_l` | numeric(19,8) | NO |
| 22 | `pt_carton_w` | numeric(19,8) | NO |
| 23 | `pt_carton_h` | numeric(19,8) | NO |
| 24 | `pt_total` | numeric(19,8) | NO |
| 25 | `pt_um_eng` | varchar(4) | NO |
| 26 | `pt_um_eng_m` | decimal(19,8) | NO |
| 27 | `pt_um_eng_d` | decimal(19,8) | NO |
| 28 | `pt_um_pur` | varchar(4) | NO |
| 29 | `pt_um_pur_m` | decimal(19,8) | NO |
| 30 | `pt_um_pur_d` | decimal(19,8) | NO |
| 31 | `pt_um_sl` | varchar(4) | NO |
| 32 | `pt_um_sl_m` | decimal(19,8) | NO |
| 33 | `pt_um_sl_d` | decimal(19,8) | NO |
| 34 | `pt_um_isu` | varchar(4) | NO |
| 35 | `pt_um_isu_m` | decimal(19,8) | NO |
| 36 | `pt_um_isu_d` | decimal(19,8) | NO |
| 37 | `pt_abc` | varchar(1) | NO |
| 38 | `pt_loc` | varchar(8) | NO |
| 39 | `pt_cyc_int` | int(10,0) | NO |
| 40 | `pt_lot_serial` | bit | NO |
| 41 | `pt_lot_grp` | varchar(15) | NO |
| 42 | `pt_keeper` | varchar(12) | NO |
| 43 | `pt_shelf_life` | int(10,0) | NO |
| 44 | `pt_wo_line` | varchar(8) | NO |
| 45 | `pt_plan_ord` | bit | NO |
| 46 | `pt_time_fence` | int(10,0) | NO |
| 47 | `pt_ord_pol` | varchar(4) | NO |
| 48 | `pt_ord_qty` | numeric(19,8) | NO |
| 49 | `pt_ord_per` | int(10,0) | NO |
| 50 | `pt_sfty_stk` | numeric(19,8) | NO |
| 51 | `pt_rop` | numeric(19,8) | NO |
| 52 | `pt_buyer` | varchar(12) | NO |
| 53 | `pt_planner` | varchar(12) | NO |
| 54 | `pt_memo_item` | bit | NO |
| 55 | `pt_max_qty` | numeric(19,8) | NO |
| 56 | `pt_vend` | varchar(8) | NO |
| 57 | `pt_pm_code` | varchar(1) | NO |
| 58 | `pt_mfg_lt` | int(10,0) | NO |
| 59 | `pt_pur_lt` | int(10,0) | NO |
| 60 | `pt_insp_rqd` | bit | NO |
| 61 | `pt_gr_lt` | int(10,0) | NO |
| 62 | `pt_phantom` | bit | NO |
| 63 | `pt_ord_min` | numeric(19,8) | NO |
| 64 | `pt_ord_mult` | numeric(19,8) | NO |
| 65 | `pt_iss_batch` | numeric(19,8) | NO |
| 66 | `pt_roll_iss` | bit | NO |
| 67 | `pt_fgov_per` | decimal(19,8) | NO |
| 68 | `pt_iss_unlimit` | bit | NO |
| 69 | `pt_level` | int(10,0) | NO |
| 70 | `pt_wf_status` | varchar(1) | NO |
| 71 | `pt_crt_by` | varchar(12) | NO |
| 72 | `pt_crt_date` | datetime | NO |
| 73 | `pt_mod_times` | int(10,0) | NO |
| 74 | `pt_mod_by` | varchar(12) | NO |
| 75 | `pt_mod_date` | datetime | NO |
| 76 | `pt_pst` | bit | NO |
| 77 | `pt_pst_by` | varchar(12) | NO |
| 78 | `pt_pst_date` | datetime | YES |
| 79 | `pt_char1` | varchar(255) | NO |
| 80 | `pt_char2` | varchar(255) | NO |
| 81 | `pt_char3` | varchar(255) | NO |
| 82 | `pt_char4` | varchar(255) | NO |
| 83 | `pt_char5` | varchar(255) | NO |
| 84 | `pt_char6` | varchar(255) | NO |
| 85 | `pt_char7` | varchar(255) | NO |
| 86 | `pt_char8` | varchar(255) | NO |
| 87 | `pt_qty1` | decimal(19,8) | NO |
| 88 | `pt_qty2` | decimal(19,8) | NO |
| 89 | `pt_qty3` | decimal(19,8) | NO |
| 90 | `pt_qty4` | decimal(19,8) | NO |
| 91 | `pt_expu_perm` | bit | NO |
| 92 | `pt_exsl_perm` | bit | NO |
| 93 | `pt_loc_pos` | varchar(18) | NO |
| 94 | `pt_eng` | varchar(12) | NO |
| 95 | `pt_custom_name` | varchar(255) | NO |
| 96 | `pt_op` | int(10,0) | NO |
| 97 | `pt_backflush` | varchar(1) | NO |
| 98 | `pt_backflush_s` | varchar(1) | NO |
| 99 | `pt_sch_type` | varchar(30) | NO |
| 100 | `pt_ovr_unmrp` | bit | NO |

### `dbo.v_pt_pm_code` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `pt_part` | varchar(30) | NO |
| 2 | `pm_code` | varchar(1) | NO |

### `dbo.v_req_sod_qty` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `req_pr_nbr` | varchar(15) | NO |
| 2 | `req_line` | int(10,0) | NO |
| 3 | `sod_part` | varchar(30) | NO |
| 4 | `sod_req` | numeric(38,6) | YES |

### `dbo.v_sdh_dn_dn` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_dn_dn` | varchar(15) | NO |
| 2 | `sdh_dn_date` | datetime | NO |
| 3 | `sdh_cust` | varchar(8) | NO |
| 4 | `sdh_dn_type` | varchar(1) | NO |
| 5 | `so_po` | varchar(255) | NO |

### `dbo.v_sdh_hist` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_flow_no` | int(10,0) | NO |
| 2 | `sdh_dn_dn` | varchar(15) | NO |
| 3 | `sdh_dnd_line` | int(10,0) | NO |
| 4 | `sdh_so_nbr` | varchar(15) | NO |
| 5 | `sdh_sod_line` | int(10,0) | NO |
| 6 | `sdh_part` | varchar(30) | NO |
| 7 | `sdh_qty_shp` | numeric(19,8) | NO |
| 8 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 9 | `sdh_um` | varchar(4) | NO |
| 10 | `sdh_dn_date` | datetime | NO |
| 11 | `sdh_cust` | varchar(8) | NO |
| 12 | `so_po` | varchar(255) | NO |
| 13 | `pt_desc1` | varchar(255) | NO |
| 14 | `si_company` | varchar(8) | NO |
| 15 | `sdh_site` | varchar(8) | NO |
| 16 | `sdh_dn_type` | varchar(1) | NO |
| 17 | `sdh_curr` | varchar(4) | NO |
| 18 | `sdh_sod_price` | decimal(19,8) | NO |
| 19 | `sdh_so_vat` | decimal(19,8) | NO |

### `dbo.v_sdh_hist_inv` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_flow_no` | int(10,0) | NO |
| 2 | `sdh_dn_dn` | varchar(15) | NO |
| 3 | `sdh_dnd_line` | int(10,0) | NO |
| 4 | `sdh_so_nbr` | varchar(15) | NO |
| 5 | `sdh_sod_line` | int(10,0) | NO |
| 6 | `sdh_part` | varchar(30) | NO |
| 7 | `sdh_qty_shp` | numeric(19,8) | NO |
| 8 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 9 | `sdh_um` | varchar(4) | NO |
| 10 | `sdh_dn_date` | datetime | NO |
| 11 | `sdh_cust` | varchar(8) | NO |
| 12 | `so_po` | varchar(255) | NO |
| 13 | `pt_desc1` | varchar(255) | NO |
| 14 | `pt_spec` | varchar(255) | NO |
| 15 | `si_company` | varchar(8) | NO |
| 16 | `sdh_site` | varchar(8) | NO |
| 17 | `sdh_dn_type` | varchar(1) | NO |
| 18 | `sdh_curr` | varchar(4) | NO |
| 19 | `sdh_sod_price` | decimal(19,8) | NO |
| 20 | `sdh_so_vat` | decimal(19,8) | NO |
| 21 | `invd_qty_inv` | numeric(38,8) | NO |
| 22 | `uninv_qty` | numeric(38,8) | YES |

### `dbo.v_sdh_hist_unar_OA` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `en_cname` | varchar(50) | NO |
| 2 | `sdh_dn_dn` | varchar(15) | NO |
| 3 | `sdh_dnd_line` | int(10,0) | NO |
| 4 | `sdh_dn_type` | varchar(1) | NO |
| 5 | `sdh_dn_date` | datetime | NO |
| 6 | `sdh_cust` | varchar(8) | NO |
| 7 | `sdh_so_nbr` | varchar(15) | NO |
| 8 | `sdh_sod_line` | int(10,0) | NO |
| 9 | `sdh_part` | varchar(30) | NO |
| 10 | `dn_addr` | varchar(255) | NO |
| 11 | `so_group` | varchar(255) | NO |
| 12 | `sdh_qty_shp` | numeric(19,8) | NO |
| 13 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 14 | `sdh_curr` | varchar(4) | NO |
| 15 | `sdh_so_vat` | decimal(19,8) | NO |
| 16 | `sdh_sod_price` | decimal(19,8) | NO |
| 17 | `sdh_ex_rate` | decimal(19,8) | NO |
| 18 | `ard_qty_pay` | numeric(38,8) | NO |
| 19 | `cm_name` | varchar(255) | NO |
| 20 | `pt_desc1` | varchar(255) | NO |
| 21 | `pt_spec` | varchar(255) | NO |
| 22 | `pl_desc` | varchar(30) | NO |
| 23 | `sdh_unar_amt` | numeric(38,6) | YES |
| 24 | `sdh_unar_unvat_amt` | numeric(38,6) | YES |
| 25 | `sdh_unar_vat_amt` | numeric(38,6) | YES |
| 26 | `sdh_unar_base_amt` | numeric(38,6) | YES |
| 27 | `sdh_unar_unvat_base_amt` | numeric(38,6) | YES |
| 28 | `sdh_unar_vat_base_amt` | numeric(38,6) | YES |
| 29 | `so_char2` | varchar(255) | NO |
| 30 | `gend_property1` | varchar(255) | NO |

### `dbo.v_sdh_hist2` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sdh_flow_no` | int(10,0) | NO |
| 2 | `sdh_dn_dn` | varchar(15) | NO |
| 3 | `sdh_dnd_line` | int(10,0) | NO |
| 4 | `sdh_so_nbr` | varchar(15) | NO |
| 5 | `sdh_sod_line` | int(10,0) | NO |
| 6 | `sdh_part` | varchar(30) | NO |
| 7 | `sdh_qty_shp` | numeric(19,8) | NO |
| 8 | `sdh_qty_spare_shp` | numeric(19,8) | NO |
| 9 | `sdh_um` | varchar(4) | NO |
| 10 | `sdh_dn_date` | datetime | NO |
| 11 | `sdh_cust` | varchar(8) | NO |
| 12 | `so_po` | varchar(255) | NO |
| 13 | `pt_desc1` | varchar(255) | NO |
| 14 | `si_company` | varchar(8) | NO |
| 15 | `sdh_site` | varchar(8) | NO |
| 16 | `sdh_dn_type` | varchar(1) | NO |
| 17 | `sdh_curr` | varchar(4) | NO |
| 18 | `sdh_sod_price` | decimal(19,8) | NO |
| 19 | `sdh_so_vat` | decimal(19,8) | NO |

### `dbo.v_so_wo` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `so_nbr` | varchar(15) | NO |
| 2 | `so_cust` | varchar(8) | NO |
| 3 | `so_addr` | varchar(255) | NO |
| 4 | `so_ord_date` | datetime | NO |
| 5 | `so_po` | varchar(255) | NO |
| 6 | `so_cr_terms` | varchar(10) | NO |
| 7 | `so_slspsn` | varchar(12) | NO |
| 8 | `so_curr` | varchar(4) | NO |
| 9 | `so_ex_rate` | decimal(19,8) | NO |
| 10 | `so_vat` | decimal(19,8) | NO |
| 11 | `so_rev` | varchar(4) | NO |
| 12 | `so_site` | varchar(8) | NO |
| 13 | `so_prog_code` | varchar(12) | NO |
| 14 | `so_doc_type` | varchar(12) | NO |
| 15 | `so_consume` | bit | NO |
| 16 | `so_fc_nbr` | varchar(15) | NO |
| 17 | `so_consignment` | bit | NO |
| 18 | `so_rmks` | varchar(255) | NO |
| 19 | `so_terms` | text(2147483647) | YES |
| 20 | `so_wf_status` | varchar(1) | NO |
| 21 | `so_crt_by` | varchar(12) | NO |
| 22 | `so_crt_date` | datetime | NO |
| 23 | `so_mod_times` | int(10,0) | NO |
| 24 | `so_mod_by` | varchar(12) | NO |
| 25 | `so_mod_date` | datetime | NO |
| 26 | `so_pst` | bit | NO |
| 27 | `so_pst_by` | varchar(12) | NO |
| 28 | `so_pst_date` | datetime | YES |
| 29 | `so_chk` | bit | NO |
| 30 | `so_chk_by` | varchar(12) | NO |
| 31 | `so_chk_date` | datetime | YES |
| 32 | `so_char1` | varchar(255) | NO |
| 33 | `so_char2` | varchar(255) | NO |
| 34 | `so_char3` | varchar(255) | NO |
| 35 | `so_char4` | varchar(255) | NO |
| 36 | `so_char5` | varchar(255) | NO |
| 37 | `so_char6` | varchar(255) | NO |
| 38 | `so_qty1` | decimal(19,8) | NO |
| 39 | `so_qty2` | decimal(19,8) | NO |
| 40 | `so_data_src` | varchar(1) | NO |
| 41 | `so_data_id` | varchar(255) | NO |
| 42 | `so_src` | varchar(2) | NO |
| 43 | `so_src_nbr` | varchar(15) | NO |
| 44 | `so_src_lot` | varchar(18) | NO |
| 45 | `so_allow` | bit | NO |
| 46 | `so_allow_by` | varchar(12) | NO |
| 47 | `so_allow_date` | datetime | YES |
| 48 | `so_po_chg` | bit | NO |
| 49 | `so_po_chg_by` | varchar(12) | NO |
| 50 | `so_po_chg_date` | datetime | YES |
| 51 | `so_po_chg_rmks` | varchar(255) | NO |
| 52 | `so_po_chk` | bit | NO |
| 53 | `so_po_chk_by` | varchar(12) | NO |
| 54 | `so_po_chk_date` | datetime | YES |
| 55 | `cm_addr` | varchar(8) | NO |
| 56 | `cm_name` | varchar(255) | NO |
| 57 | `cm_sort` | varchar(50) | NO |
| 58 | `cm_txt_inv` | varchar(255) | NO |
| 59 | `cm_txt_run` | varchar(255) | NO |
| 60 | `cm_txt_ship` | varchar(255) | NO |
| 61 | `cm_www` | varchar(80) | NO |
| 62 | `cm_attn1` | varchar(24) | NO |
| 63 | `cm_pos1` | varchar(30) | NO |
| 64 | `cm_tele1` | varchar(50) | NO |
| 65 | `cm_fax1` | varchar(50) | NO |
| 66 | `cm_email1` | varchar(50) | NO |
| 67 | `cm_attn2` | varchar(24) | NO |
| 68 | `cm_pos2` | varchar(30) | NO |
| 69 | `cm_tele2` | varchar(50) | NO |
| 70 | `cm_fax2` | varchar(50) | NO |
| 71 | `cm_email2` | varchar(50) | NO |
| 72 | `cm_attn3` | varchar(24) | NO |
| 73 | `cm_pos3` | varchar(30) | NO |
| 74 | `cm_tele3` | varchar(50) | NO |
| 75 | `cm_fax3` | varchar(50) | NO |
| 76 | `cm_email3` | varchar(50) | NO |
| 77 | `cm_attn4` | varchar(24) | NO |
| 78 | `cm_tele4` | varchar(50) | NO |
| 79 | `cm_fax4` | varchar(50) | NO |
| 80 | `cm_email4` | varchar(50) | NO |
| 81 | `cm_pos4` | varchar(30) | NO |
| 82 | `cm_cmmt` | varchar(255) | NO |
| 83 | `cm_slspsn` | varchar(12) | NO |
| 84 | `cm_kind` | varchar(1) | NO |
| 85 | `cm_type` | varchar(30) | NO |
| 86 | `cm_region` | varchar(30) | NO |
| 87 | `cm_quot_type` | varchar(1) | NO |
| 88 | `cm_vat_method` | varchar(1) | NO |
| 89 | `cm_cr_terms` | varchar(10) | NO |
| 90 | `cm_chk_day` | int(10,0) | NO |
| 91 | `cm_curr` | varchar(4) | NO |
| 92 | `cm_cr_hold` | bit | NO |
| 93 | `cm_disc` | decimal(19,8) | NO |
| 94 | `cm_vat` | decimal(19,8) | NO |
| 95 | `cm_spare_pct` | decimal(19,8) | NO |
| 96 | `cm_tol_pct` | decimal(19,8) | NO |
| 97 | `cm_consignment` | bit | NO |
| 98 | `cm_reg_code` | varchar(30) | NO |
| 99 | `cm_bank` | varchar(255) | NO |
| 100 | `cm_bank_acct` | varchar(30) | NO |
| 101 | `cm_comp_owner` | varchar(30) | NO |
| 102 | `cm_reg_fund` | decimal(19,8) | NO |
| 103 | `cm_tunrover` | decimal(19,8) | NO |
| 104 | `cm_open_date` | datetime | YES |
| 105 | `cm_employees` | int(10,0) | NO |
| 106 | `cm_limit_project` | varchar(30) | NO |
| 107 | `cm_credit1` | numeric(19,8) | NO |
| 108 | `cm_credit2` | numeric(19,8) | NO |
| 109 | `cm_max_days1` | int(10,0) | NO |
| 110 | `cm_max_days2` | int(10,0) | NO |
| 111 | `cm_ac_code_pre` | varchar(15) | NO |
| 112 | `cm_ac_code_ar` | varchar(15) | NO |
| 113 | `cm_ac_code_income` | varchar(15) | NO |
| 114 | `cm_ac_code_cost` | varchar(15) | NO |
| 115 | `cm_crt_by` | varchar(12) | NO |
| 116 | `cm_crt_date` | datetime | NO |
| 117 | `cm_mod_times` | int(10,0) | NO |
| 118 | `cm_mod_by` | varchar(12) | NO |
| 119 | `cm_mod_date` | datetime | NO |
| 120 | `cm_pst` | bit | NO |
| 121 | `cm_pst_by` | varchar(12) | NO |
| 122 | `cm_pst_date` | datetime | YES |
| 123 | `cm_wf_status` | varchar(1) | NO |
| 124 | `cm_char1` | varchar(255) | NO |
| 125 | `cm_char2` | varchar(255) | NO |
| 126 | `cm_char3` | varchar(255) | NO |
| 127 | `cm_char4` | varchar(255) | NO |
| 128 | `cm_char5` | varchar(255) | NO |
| 129 | `cm_char6` | varchar(255) | NO |
| 130 | `cm_qty1` | decimal(19,8) | NO |
| 131 | `cm_qty2` | decimal(19,8) | NO |
| 132 | `cm_ast_code` | varchar(15) | NO |
| 133 | `cm_headq` | varchar(8) | NO |
| 134 | `cm_dna_req` | bit | NO |
| 135 | `cm_invalid` | varchar(1) | NO |
| 136 | `cm_invalid_by` | varchar(12) | NO |
| 137 | `cm_invalid_date` | datetime | YES |
| 138 | `cm_ac_code_as` | varchar(15) | NO |
| 139 | `cm_cu_area` | varchar(30) | NO |
| 140 | `cm_cu_curr` | varchar(30) | NO |
| 141 | `cm_price_type` | varchar(1) | NO |
| 142 | `cm_inv_type` | varchar(1) | NO |
| 143 | `cm_tot_qty_price` | bit | NO |
| 144 | `cm_price_vat` | varchar(1) | NO |
| 145 | `cm_chk` | bit | NO |
| 146 | `cm_chk_by` | varchar(12) | NO |
| 147 | `cm_chk_date` | datetime | YES |
| 148 | `cm_template` | varchar(12) | NO |

### `dbo.v_sod_det_cust_part` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `sod_nbr` | varchar(15) | NO |
| 2 | `sod_line` | int(10,0) | NO |
| 3 | `sod_part` | varchar(30) | NO |
| 4 | `sod_cust_part` | varchar(80) | NO |
| 5 | `cp_cust_desc` | varchar(255) | NO |
| 6 | `cp_char1` | varchar(255) | NO |
| 7 | `cp_char2` | varchar(255) | NO |

### `dbo.v_tpt_barcode_fr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `bc_user` | varchar(12) | NO |
| 2 | `bc_flow` | int(10,0) | NO |
| 3 | `bc_key1` | varchar(30) | NO |
| 4 | `bc_key2` | varchar(30) | NO |
| 5 | `bc_key3` | varchar(30) | NO |
| 6 | `bc_key4` | varchar(30) | NO |
| 7 | `bc_key5` | varchar(30) | NO |
| 8 | `bc_code` | varchar(2000) | NO |
| 9 | `bc_img` | image(2147483647) | YES |
| 10 | `bc_value1` | varchar(50) | NO |
| 11 | `bc_value2` | varchar(50) | NO |
| 12 | `bc_value3` | varchar(50) | NO |
| 13 | `bc_value4` | varchar(50) | NO |
| 14 | `bc_value5` | varchar(50) | NO |
| 15 | `bc_value6` | varchar(50) | NO |
| 16 | `bc_value7` | varchar(50) | NO |
| 17 | `bc_value8` | varchar(50) | NO |
| 18 | `bc_value9` | varchar(50) | NO |
| 19 | `bc_qty1` | numeric(19,8) | NO |
| 20 | `bc_qty2` | numeric(19,8) | NO |
| 21 | `bc_qty3` | numeric(19,8) | NO |
| 22 | `bc_qty4` | numeric(19,8) | NO |
| 23 | `bc_qty5` | numeric(19,8) | NO |
| 24 | `bc_qty6` | numeric(19,8) | NO |
| 25 | `bc_qty7` | numeric(19,8) | NO |
| 26 | `bc_qty8` | numeric(19,8) | NO |
| 27 | `bc_qty9` | numeric(19,8) | NO |
| 28 | `bc_date1` | datetime | YES |
| 29 | `bc_date2` | datetime | YES |
| 30 | `bc_date3` | datetime | YES |
| 31 | `bc_date4` | datetime | YES |
| 32 | `bc_text1` | varchar(50) | NO |
| 33 | `bc_text2` | varchar(50) | NO |
| 34 | `bc_text3` | varchar(50) | NO |
| 35 | `bc_text4` | varchar(50) | NO |
| 36 | `line` | int(10,0) | YES |

### `dbo.v_tpt_barcode_iqc` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `bc_user` | varchar(12) | NO |
| 2 | `bc_flow` | int(10,0) | NO |
| 3 | `bc_key1` | varchar(30) | NO |
| 4 | `bc_key2` | varchar(30) | NO |
| 5 | `bc_key3` | varchar(30) | NO |
| 6 | `bc_key4` | varchar(30) | NO |
| 7 | `bc_key5` | varchar(30) | NO |
| 8 | `bc_code` | varchar(2000) | NO |
| 9 | `bc_img` | image(2147483647) | YES |
| 10 | `bc_value1` | varchar(50) | NO |
| 11 | `bc_value2` | varchar(50) | NO |
| 12 | `bc_value3` | varchar(50) | NO |
| 13 | `bc_value4` | varchar(50) | NO |
| 14 | `bc_value5` | varchar(50) | NO |
| 15 | `bc_value6` | varchar(50) | NO |
| 16 | `bc_value7` | varchar(50) | NO |
| 17 | `bc_value8` | varchar(50) | NO |
| 18 | `bc_value9` | varchar(50) | NO |
| 19 | `bc_qty1` | numeric(19,8) | NO |
| 20 | `bc_qty2` | numeric(19,8) | NO |
| 21 | `bc_qty3` | numeric(19,8) | NO |
| 22 | `bc_qty4` | numeric(19,8) | NO |
| 23 | `bc_qty5` | numeric(19,8) | NO |
| 24 | `bc_qty6` | numeric(19,8) | NO |
| 25 | `bc_qty7` | numeric(19,8) | NO |
| 26 | `bc_qty8` | numeric(19,8) | NO |
| 27 | `bc_qty9` | numeric(19,8) | NO |
| 28 | `bc_date1` | datetime | YES |
| 29 | `bc_date2` | datetime | YES |
| 30 | `bc_date3` | datetime | YES |
| 31 | `bc_date4` | datetime | YES |
| 32 | `bc_text1` | varchar(50) | NO |
| 33 | `bc_text2` | varchar(50) | NO |
| 34 | `bc_text3` | varchar(50) | NO |
| 35 | `bc_text4` | varchar(50) | NO |
| 36 | `line` | int(10,0) | YES |

### `dbo.v_tpt_barocde` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `bc_user` | varchar(12) | NO |
| 2 | `bc_flow` | int(10,0) | NO |
| 3 | `bc_key1` | varchar(30) | NO |
| 4 | `bc_key2` | varchar(30) | NO |
| 5 | `bc_key3` | int(10,0) | YES |
| 6 | `bc_key4` | varchar(30) | NO |
| 7 | `bc_key5` | varchar(30) | NO |
| 8 | `bc_code` | varchar(2000) | NO |
| 9 | `bc_img` | image(2147483647) | YES |

### `dbo.v_tr_hist` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tr_trnbr` | int(10,0) | NO |
| 2 | `tr_part` | varchar(30) | NO |
| 3 | `tr_type` | varchar(8) | NO |
| 4 | `tr_date` | datetime | NO |
| 5 | `tr_effdate` | datetime | NO |
| 6 | `tr_site` | varchar(8) | NO |
| 7 | `tr_loc` | varchar(8) | NO |
| 8 | `tr_qty_loc` | numeric(19,8) | NO |
| 9 | `tr_um` | varchar(4) | NO |
| 10 | `tr_um_rate_m` | decimal(19,8) | NO |
| 11 | `tr_um_rate_d` | decimal(19,8) | NO |
| 12 | `tr_um_stk` | varchar(4) | NO |
| 13 | `tr_nbr` | varchar(15) | NO |
| 14 | `tr_line` | int(10,0) | NO |
| 15 | `tr_price` | decimal(19,8) | NO |
| 16 | `tr_curr` | varchar(4) | NO |
| 17 | `tr_ex_rate` | decimal(19,8) | NO |
| 18 | `tr_so_job` | varchar(15) | NO |
| 19 | `tr_lot` | varchar(18) | NO |
| 20 | `tr_ref` | varchar(15) | NO |
| 21 | `tr_ref_line` | int(10,0) | NO |
| 22 | `tr_addr` | varchar(8) | NO |
| 23 | `tr_lotserial` | varchar(18) | NO |
| 24 | `tr_ord_rev` | varchar(4) | NO |
| 25 | `tr_grade` | varchar(2) | NO |
| 26 | `tr_rmks` | varchar(255) | NO |
| 27 | `tr_userid` | varchar(12) | NO |
| 28 | `tr_mtl_tl` | decimal(19,8) | NO |
| 29 | `tr_mtl_ll` | decimal(19,8) | NO |
| 30 | `tr_lbr_tl` | decimal(19,8) | NO |
| 31 | `tr_lbr_ll` | decimal(19,8) | NO |
| 32 | `tr_bdn_tl` | decimal(19,8) | NO |
| 33 | `tr_bdn_ll` | decimal(19,8) | NO |
| 34 | `tr_sub_tl` | decimal(19,8) | NO |
| 35 | `tr_sub_ll` | decimal(19,8) | NO |
| 36 | `tr_mtl_amt` | decimal(19,8) | NO |
| 37 | `tr_lbr_amt` | decimal(19,8) | NO |
| 38 | `tr_bdn_amt` | decimal(19,8) | NO |
| 39 | `tr_sub_amt` | decimal(19,8) | NO |
| 40 | `tr_mtl_amt_ll` | decimal(19,8) | NO |
| 41 | `tr_lbr_amt_ll` | decimal(19,8) | NO |
| 42 | `tr_bdn_amt_ll` | decimal(19,8) | NO |
| 43 | `tr_sub_amt_ll` | decimal(19,8) | NO |
| 44 | `tr_cost_flag` | bit | NO |
| 45 | `tr_char1` | varchar(255) | NO |
| 46 | `tr_char2` | varchar(255) | NO |
| 47 | `tr_char3` | varchar(255) | NO |
| 48 | `tr_char4` | varchar(255) | NO |
| 49 | `tr_char5` | varchar(255) | NO |
| 50 | `tr_char6` | varchar(255) | NO |
| 51 | `tr_qty1` | decimal(19,8) | NO |
| 52 | `tr_qty2` | decimal(19,8) | NO |

### `dbo.v_tr_ref_line` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `tr_type` | varchar(8) | NO |
| 2 | `tr_effdate` | datetime | NO |
| 3 | `tr_ref` | varchar(15) | NO |
| 4 | `tr_ref_line` | int(10,0) | NO |
| 5 | `tr_nbr` | varchar(15) | NO |
| 6 | `tr_part` | varchar(30) | NO |
| 7 | `pt_desc1` | varchar(255) | NO |
| 8 | `pt_spec` | varchar(255) | NO |
| 9 | `tr_loc` | varchar(8) | NO |
| 10 | `loc_desc` | varchar(30) | NO |
| 11 | `tr_qty_loc` | numeric(30,8) | YES |
| 12 | `tr_lotserial` | varchar(18) | NO |

### `dbo.v_user_vend_cust` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vd_addr` | varchar(12) | NO |
| 2 | `vd_sort` | varchar(50) | NO |
| 3 | `vd_buyer` | varchar(12) | NO |
| 4 | `addr_type` | varchar(1) | NO |

### `dbo.v_usr_mstr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `usr_user` | varchar(12) | NO |
| 2 | `usr_name` | varchar(30) | NO |
| 3 | `usr_group` | varchar(12) | NO |
| 4 | `usr_dept` | varchar(10) | NO |
| 5 | `usr_password` | varchar(50) | NO |
| 6 | `usr_lib_path` | varchar(80) | NO |
| 7 | `usr_def_site` | varchar(8) | NO |
| 8 | `usr_warning_circle` | int(10,0) | NO |
| 9 | `usr_employee` | bit | NO |
| 10 | `usr_lock` | bit | NO |
| 11 | `usr_out` | bit | NO |
| 12 | `usr_agent` | varchar(12) | NO |
| 13 | `usr_allow_ip` | varchar(255) | NO |
| 14 | `usr_crt_by` | varchar(12) | NO |
| 15 | `usr_crt_date` | datetime | NO |
| 16 | `usr_char1` | varchar(255) | NO |
| 17 | `usr_char2` | varchar(255) | NO |
| 18 | `usr_char3` | varchar(255) | NO |
| 19 | `usr_char4` | varchar(255) | NO |
| 20 | `usr_char5` | varchar(255) | NO |
| 21 | `usr_char6` | varchar(255) | NO |
| 22 | `usr_qty1` | decimal(19,8) | NO |
| 23 | `usr_qty2` | decimal(19,8) | NO |
| 24 | `usr_tele` | varchar(50) | NO |
| 25 | `usr_mobile` | varchar(50) | NO |
| 26 | `usr_email` | varchar(50) | NO |
| 27 | `usr_qq` | varchar(30) | NO |
| 28 | `usr_wechat` | varchar(50) | NO |
| 29 | `usr_other` | varchar(50) | NO |
| 30 | `usr_pos` | varchar(30) | NO |
| 31 | `usr_prog_cnt` | int(10,0) | NO |
| 32 | `usr_time_lmt` | int(10,0) | NO |
| 33 | `usr_lang` | varchar(10) | NO |

### `dbo.v_vd_mstr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vd_addr` | varchar(8) | NO |
| 2 | `vd_sort` | varchar(50) | NO |
| 3 | `vd_buyer` | varchar(12) | NO |
| 4 | `vd_curr` | varchar(4) | NO |
| 5 | `usr_name` | varchar(30) | NO |
| 6 | `vd_kind` | varchar(1) | NO |
| 7 | `vd_kind_desc` | varchar(14) | NO |
| 8 | `vd_strategic` | varchar(10) | NO |

### `dbo.v_vend_cust_line` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vd_type` | varchar(1) | NO |
| 2 | `vd_addr` | varchar(8) | NO |
| 3 | `vd_sort` | varchar(50) | NO |
| 4 | `vd_pst` | int(10,0) | NO |

### `dbo.v_vend_SCM` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `vd_addr` | varchar(8) | NO |
| 2 | `vd_name` | varchar(255) | NO |
| 3 | `vd_sort` | varchar(50) | NO |
| 4 | `vd_txt` | varchar(255) | NO |
| 5 | `vd_attn` | varchar(24) | NO |
| 6 | `vd_tele` | varchar(50) | NO |
| 7 | `vd_fax` | varchar(50) | NO |
| 8 | `vd_email` | varchar(50) | NO |
| 9 | `vd_attn2` | varchar(24) | NO |
| 10 | `vd_tele2` | varchar(50) | NO |
| 11 | `vd_fax2` | varchar(50) | NO |
| 12 | `vd_email2` | varchar(50) | NO |
| 13 | `vd_www` | varchar(80) | NO |
| 14 | `vd_rmks` | varchar(255) | NO |
| 15 | `vd_buyer` | varchar(12) | NO |
| 16 | `vd_curr` | varchar(4) | NO |
| 17 | `vd_vat` | decimal(19,8) | NO |
| 18 | `vd_cr_terms` | varchar(10) | NO |
| 19 | `vd_spare_pct` | decimal(19,8) | NO |
| 20 | `vd_tol_pct` | decimal(19,8) | NO |
| 21 | `vd_service` | int(10,0) | NO |
| 22 | `vd_quot_type` | varchar(1) | NO |
| 23 | `vd_inv_type` | varchar(1) | NO |
| 24 | `vd_vat_method` | varchar(1) | NO |
| 25 | `vd_kind` | varchar(1) | NO |
| 26 | `vd_bid_settle` | bit | NO |
| 27 | `vd_reg_code` | varchar(30) | NO |
| 28 | `vd_bank` | varchar(255) | NO |
| 29 | `vd_bank_acct` | varchar(30) | NO |
| 30 | `vd_comp_owner` | varchar(30) | NO |
| 31 | `vd_reg_fund` | decimal(19,8) | NO |
| 32 | `vd_tunrover` | decimal(19,8) | NO |
| 33 | `vd_open_date` | datetime | YES |
| 34 | `vd_employees` | int(10,0) | NO |
| 35 | `vd_hold` | bit | NO |
| 36 | `vd_ap_ac` | varchar(15) | NO |
| 37 | `vd_tap_ac` | varchar(15) | NO |
| 38 | `vd_sub_ac` | varchar(15) | NO |
| 39 | `vd_comm_ac` | varchar(15) | NO |
| 40 | `vd_wf_status` | varchar(1) | NO |
| 41 | `vd_crt_by` | varchar(12) | NO |
| 42 | `vd_crt_date` | datetime | NO |
| 43 | `vd_mod_times` | int(10,0) | NO |
| 44 | `vd_mod_by` | varchar(12) | NO |
| 45 | `vd_mod_date` | datetime | NO |
| 46 | `vd_pst` | bit | NO |
| 47 | `vd_pst_by` | varchar(12) | NO |
| 48 | `vd_pst_date` | datetime | YES |
| 49 | `vd_char1` | varchar(255) | NO |
| 50 | `vd_char2` | varchar(255) | NO |
| 51 | `vd_char3` | varchar(255) | NO |
| 52 | `vd_char4` | varchar(255) | NO |
| 53 | `vd_char5` | varchar(255) | NO |
| 54 | `vd_char6` | varchar(255) | NO |
| 55 | `vd_qty1` | decimal(19,8) | NO |
| 56 | `vd_qty2` | decimal(19,8) | NO |
| 57 | `vd_invalid` | varchar(1) | NO |
| 58 | `vd_invalid_by` | varchar(12) | NO |
| 59 | `vd_invalid_date` | datetime | YES |
| 60 | `vd_mtl_sales` | varchar(30) | NO |
| 61 | `vd_mtl_rate` | numeric(19,8) | NO |
| 62 | `vd_allow` | bit | NO |
| 63 | `vd_allow_by` | varchar(12) | NO |
| 64 | `vd_allow_date` | datetime | YES |
| 65 | `vd_3c` | bit | NO |
| 66 | `vd_open` | bit | NO |
| 67 | `vd_isinternal` | bit | NO |
| 68 | `vd_strategic` | varchar(1) | NO |

### `dbo.v_wo_sod_part` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wo_site` | varchar(8) | NO |
| 2 | `wo_nbr` | varchar(15) | NO |
| 3 | `wo_lot` | varchar(30) | YES |
| 4 | `wo_part` | varchar(30) | NO |
| 5 | `wo_qty_ord` | numeric(20,8) | YES |
| 6 | `wo_due_date` | datetime | NO |
| 7 | `pt_desc1` | varchar(255) | NO |
| 8 | `pt_spec` | varchar(255) | NO |

### `dbo.v_wo_top_nbr` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wo_nbr` | varchar(15) | NO |
| 2 | `wo_lot` | varchar(18) | NO |
| 3 | `wo_type` | varchar(1) | NO |
| 4 | `wo_type2` | varchar(1) | NO |
| 5 | `wo_part` | varchar(30) | NO |
| 6 | `wo_qty_ord` | numeric(19,8) | NO |
| 7 | `wo_qty_comp` | numeric(19,8) | NO |
| 8 | `wo_qty_rjct` | numeric(19,8) | NO |
| 9 | `wo_line` | varchar(8) | NO |
| 10 | `wo_ord_date` | datetime | NO |
| 11 | `wo_rel_date` | datetime | NO |
| 12 | `wo_due_date` | datetime | NO |
| 13 | `wo_close_by` | varchar(12) | NO |
| 14 | `wo_close_date` | datetime | YES |
| 15 | `wo_status` | varchar(1) | NO |
| 16 | `wo_so_nbr` | varchar(15) | NO |
| 17 | `wo_so_line` | int(10,0) | NO |
| 18 | `wo_fgov_per` | decimal(19,8) | NO |
| 19 | `wo_rmks` | varchar(255) | NO |
| 20 | `wo_other_rmks` | text(2147483647) | YES |
| 21 | `wo_site` | varchar(8) | NO |
| 22 | `wo_wf_staus` | varchar(1) | NO |
| 23 | `wo_prog_code` | varchar(12) | NO |
| 24 | `wo_doc_code` | varchar(12) | NO |
| 25 | `wo_crt_by` | varchar(12) | NO |
| 26 | `wo_crt_date` | datetime | NO |
| 27 | `wo_mod_times` | int(10,0) | NO |
| 28 | `wo_mod_by` | varchar(12) | NO |
| 29 | `wo_mod_date` | datetime | NO |
| 30 | `wo_char1` | varchar(255) | NO |
| 31 | `wo_char2` | varchar(255) | NO |
| 32 | `wo_char3` | varchar(255) | NO |
| 33 | `wo_char4` | varchar(255) | NO |
| 34 | `wo_char5` | varchar(255) | NO |
| 35 | `wo_char6` | varchar(255) | NO |
| 36 | `wo_qty1` | decimal(19,8) | NO |
| 37 | `wo_qty2` | decimal(19,8) | NO |
| 38 | `wo_src` | varchar(2) | NO |
| 39 | `wo_src_nbr` | varchar(15) | NO |
| 40 | `wo_src_lot` | varchar(18) | NO |
| 41 | `wo_sod_conf` | bit | NO |
| 42 | `wo_sod_conf_by` | varchar(12) | NO |
| 43 | `wo_sod_conf_date` | datetime | YES |
| 44 | `wo_close_reason` | varchar(255) | NO |
| 45 | `wo_data_src` | varchar(1) | NO |
| 46 | `wo_data_id` | varchar(255) | NO |
| 47 | `wo_seq` | varchar(15) | NO |
| 48 | `tmp_nbr` | varchar(255) | YES |
| 49 | `top_nbr` | varchar(15) | NO |
| 50 | `top_lot` | varchar(30) | NO |
| 51 | `top_part` | varchar(30) | NO |
| 52 | `top_qty_ord` | numeric(38,7) | YES |
| 53 | `top_so_cust` | varchar(8) | NO |
| 54 | `top_so_po` | varchar(255) | NO |
| 55 | `pt_desc1` | varchar(255) | NO |
| 56 | `pt_desc2` | varchar(255) | NO |
| 57 | `pt_um` | varchar(4) | NO |
| 58 | `pt_custom_code` | varchar(50) | NO |
| 59 | `pt_custom_name` | varchar(255) | NO |
| 60 | `pt_spec` | varchar(255) | NO |
| 61 | `par_desc1` | varchar(255) | NO |
| 62 | `par_desc2` | varchar(255) | NO |
| 63 | `par_um` | varchar(4) | NO |
| 64 | `par_custom_code` | varchar(50) | NO |
| 65 | `par_custom_name` | varchar(255) | NO |
| 66 | `par_spec` | varchar(255) | NO |
| 67 | `cm_sort` | varchar(50) | NO |

### `dbo.v_wo_wod_part` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wo_nbr` | varchar(15) | NO |
| 2 | `wo_lot` | varchar(18) | NO |
| 3 | `wo_type` | varchar(1) | NO |
| 4 | `wo_type2` | varchar(1) | NO |
| 5 | `wo_part` | varchar(30) | NO |
| 6 | `wo_qty_ord` | numeric(19,8) | NO |
| 7 | `wo_qty_comp` | numeric(19,8) | NO |
| 8 | `wo_qty_rjct` | numeric(19,8) | NO |
| 9 | `wo_line` | varchar(8) | NO |
| 10 | `wo_ord_date` | datetime | NO |
| 11 | `wo_rel_date` | datetime | NO |
| 12 | `wo_due_date` | datetime | NO |
| 13 | `wo_close_by` | varchar(12) | NO |
| 14 | `wo_close_date` | datetime | YES |
| 15 | `wo_status` | varchar(1) | NO |
| 16 | `wo_so_nbr` | varchar(15) | NO |
| 17 | `wo_so_line` | int(10,0) | NO |
| 18 | `wo_fgov_per` | decimal(19,8) | NO |
| 19 | `wo_rmks` | varchar(255) | NO |
| 20 | `wo_other_rmks` | text(2147483647) | YES |
| 21 | `wo_site` | varchar(8) | NO |
| 22 | `wo_wf_staus` | varchar(1) | NO |
| 23 | `wo_prog_code` | varchar(12) | NO |
| 24 | `wo_doc_code` | varchar(12) | NO |
| 25 | `wo_crt_by` | varchar(12) | NO |
| 26 | `wo_crt_date` | datetime | NO |
| 27 | `wo_mod_times` | int(10,0) | NO |
| 28 | `wo_mod_by` | varchar(12) | NO |
| 29 | `wo_mod_date` | datetime | NO |
| 30 | `wo_char1` | varchar(255) | NO |
| 31 | `wo_char2` | varchar(255) | NO |
| 32 | `wo_char3` | varchar(255) | NO |
| 33 | `wo_char4` | varchar(255) | NO |
| 34 | `wo_char5` | varchar(255) | NO |
| 35 | `wo_char6` | varchar(255) | NO |
| 36 | `wo_qty1` | decimal(19,8) | NO |
| 37 | `wo_qty2` | decimal(19,8) | NO |
| 38 | `wo_src` | varchar(2) | NO |
| 39 | `wo_src_nbr` | varchar(15) | NO |
| 40 | `wo_src_lot` | varchar(18) | NO |
| 41 | `wo_sod_conf` | bit | NO |
| 42 | `wo_sod_conf_by` | varchar(12) | NO |
| 43 | `wo_sod_conf_date` | datetime | YES |
| 44 | `wo_close_reason` | varchar(255) | NO |
| 45 | `wo_data_src` | varchar(1) | NO |
| 46 | `wo_data_id` | varchar(255) | NO |
| 47 | `wo_seq` | varchar(15) | NO |
| 48 | `wod_nbr` | varchar(15) | YES |
| 49 | `wod_lot` | varchar(18) | YES |
| 50 | `wod_seq` | int(10,0) | YES |
| 51 | `wod_part` | varchar(30) | YES |
| 52 | `wod_loc` | varchar(8) | YES |
| 53 | `wod_op` | int(10,0) | YES |
| 54 | `wod_incl_sub` | bit | YES |
| 55 | `wod_alt` | bit | YES |
| 56 | `wod_alt_seq` | int(10,0) | YES |
| 57 | `wod_roll_iss` | bit | YES |
| 58 | `wod_qty_per_m` | numeric(19,8) | YES |
| 59 | `wod_qty_per_d` | numeric(19,8) | YES |
| 60 | `wod_qty_req_std` | numeric(19,8) | YES |
| 61 | `wod_qty_req_scr` | numeric(19,8) | YES |
| 62 | `wod_qty_req` | numeric(19,8) | YES |
| 63 | `wod_due_date` | datetime | YES |
| 64 | `wod_qty_iss` | numeric(19,8) | YES |
| 65 | `wod_ovr_iss` | numeric(19,8) | YES |
| 66 | `wod_qty_adj` | numeric(19,8) | YES |
| 67 | `wod_qty_rtng` | numeric(19,8) | YES |
| 68 | `wod_qty_rtnv` | numeric(19,8) | YES |
| 69 | `wod_qty_rtns` | numeric(19,8) | YES |
| 70 | `wod_qty_scr` | numeric(19,8) | YES |
| 71 | `wod_qty_con` | numeric(19,8) | YES |
| 72 | `wod_qty_alloc` | numeric(19,8) | YES |
| 73 | `wod_qty_pts_m` | numeric(19,8) | YES |
| 74 | `wod_qty_pts_d` | numeric(19,8) | YES |
| 75 | `wod_mrp` | bit | YES |
| 76 | `wod_rmks` | varchar(255) | YES |
| 77 | `wod_crt_by` | varchar(12) | YES |
| 78 | `wod_crt_date` | datetime | YES |
| 79 | `wod_mod_times` | int(10,0) | YES |
| 80 | `wod_mod_by` | varchar(12) | YES |
| 81 | `wod_mod_date` | datetime | YES |
| 82 | `wod_char1` | varchar(255) | YES |
| 83 | `wod_char2` | varchar(255) | YES |
| 84 | `wod_char3` | varchar(255) | YES |
| 85 | `wod_char4` | varchar(255) | YES |
| 86 | `wod_char5` | varchar(255) | YES |
| 87 | `wod_char6` | varchar(255) | YES |
| 88 | `wod_qty1` | decimal(19,8) | YES |
| 89 | `wod_qty2` | decimal(19,8) | YES |
| 90 | `wod_sodb_seq` | int(10,0) | YES |
| 91 | `wod_qty_org` | numeric(19,8) | YES |
| 92 | `wod_wire_req` | varchar(1000) | YES |
| 93 | `wod_ps_rmks` | varchar(1000) | YES |
| 94 | `wod_data_src` | varchar(1) | YES |
| 95 | `wod_data_id` | varchar(255) | YES |
| 96 | `par_desc1` | varchar(255) | NO |
| 97 | `par_um` | varchar(4) | NO |
| 98 | `comp_desc1` | varchar(255) | YES |
| 99 | `comp_um` | varchar(4) | YES |
| 100 | `par_desc2` | varchar(255) | NO |
| 101 | `comp_desc2` | varchar(255) | YES |
| 102 | `so_cust` | varchar(8) | NO |
| 103 | `so_po` | varchar(255) | NO |
| 104 | `so_slspsn` | varchar(12) | NO |
| 105 | `cm_name` | varchar(255) | NO |
| 106 | `sod_cust_part` | varchar(80) | NO |
| 107 | `cp_cust_desc` | varchar(255) | NO |
| 108 | `cp_char1` | varchar(255) | NO |
| 109 | `cp_char2` | varchar(255) | NO |
| 110 | `cp_char3` | varchar(255) | NO |
| 111 | `cp_char4` | varchar(255) | NO |
| 112 | `cp_char5` | varchar(255) | NO |
| 113 | `cp_char6` | varchar(255) | NO |
| 114 | `cp_qty1` | decimal(19,8) | NO |
| 115 | `cp_qty2` | decimal(19,8) | NO |
| 116 | `sod_char1` | varchar(255) | NO |
| 117 | `sod_char2` | varchar(255) | NO |
| 118 | `sod_char3` | varchar(255) | NO |
| 119 | `sod_char4` | varchar(255) | NO |
| 120 | `sod_char5` | varchar(255) | NO |
| 121 | `sod_char6` | varchar(255) | NO |
| 122 | `sod_qty1` | decimal(19,8) | NO |
| 123 | `sod_qty2` | decimal(19,8) | NO |
| 124 | `cm_slspsn` | varchar(12) | NO |
| 125 | `cm_sort` | varchar(50) | NO |

### `dbo.v_wod_ptp3` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wod_nbr` | varchar(15) | NO |
| 2 | `wod_lot` | varchar(18) | NO |
| 3 | `wod_seq` | int(10,0) | NO |
| 4 | `wod_part` | varchar(30) | NO |
| 5 | `wod_loc` | varchar(8) | NO |
| 6 | `wod_op` | int(10,0) | NO |
| 7 | `wod_incl_sub` | bit | NO |
| 8 | `wod_alt` | bit | NO |
| 9 | `wod_alt_seq` | int(10,0) | NO |
| 10 | `wod_roll_iss` | bit | NO |
| 11 | `wod_qty_per_m` | numeric(19,8) | NO |
| 12 | `wod_qty_per_d` | numeric(19,8) | NO |
| 13 | `wod_qty_req_std` | numeric(19,8) | NO |
| 14 | `wod_qty_req_scr` | numeric(19,8) | NO |
| 15 | `wod_qty_req` | numeric(19,8) | NO |
| 16 | `wod_due_date` | datetime | NO |
| 17 | `wod_qty_iss` | numeric(19,8) | NO |
| 18 | `wod_ovr_iss` | numeric(19,8) | NO |
| 19 | `wod_qty_adj` | numeric(19,8) | NO |
| 20 | `wod_qty_rtng` | numeric(19,8) | NO |
| 21 | `wod_qty_rtnv` | numeric(19,8) | NO |
| 22 | `wod_qty_rtns` | numeric(19,8) | NO |
| 23 | `wod_qty_scr` | numeric(19,8) | NO |
| 24 | `wod_qty_con` | numeric(19,8) | NO |
| 25 | `wod_qty_alloc` | numeric(19,8) | NO |
| 26 | `wod_qty_pts_m` | numeric(19,8) | NO |
| 27 | `wod_qty_pts_d` | numeric(19,8) | NO |
| 28 | `wod_mrp` | bit | NO |
| 29 | `wod_rmks` | varchar(255) | NO |
| 30 | `wod_crt_by` | varchar(12) | NO |
| 31 | `wod_crt_date` | datetime | NO |
| 32 | `wod_mod_times` | int(10,0) | NO |
| 33 | `wod_mod_by` | varchar(12) | NO |
| 34 | `wod_mod_date` | datetime | NO |
| 35 | `wod_char1` | varchar(255) | NO |
| 36 | `wod_char2` | varchar(255) | NO |
| 37 | `wod_char3` | varchar(255) | NO |
| 38 | `wod_char4` | varchar(255) | NO |
| 39 | `wod_char5` | varchar(255) | NO |
| 40 | `wod_char6` | varchar(255) | NO |
| 41 | `wod_qty1` | decimal(19,8) | NO |
| 42 | `wod_qty2` | decimal(19,8) | NO |
| 43 | `wod_sodb_seq` | int(10,0) | NO |
| 44 | `wod_qty_org` | numeric(19,8) | NO |
| 45 | `wod_wire_req` | varchar(1000) | NO |
| 46 | `wod_ps_rmks` | varchar(1000) | NO |
| 47 | `wod_data_src` | varchar(1) | NO |
| 48 | `wod_data_id` | varchar(255) | NO |
| 49 | `wo_nbr` | varchar(15) | NO |
| 50 | `wo_lot` | varchar(18) | NO |
| 51 | `wo_type` | varchar(1) | NO |
| 52 | `wo_type2` | varchar(1) | NO |
| 53 | `wo_part` | varchar(30) | NO |
| 54 | `wo_qty_ord` | numeric(19,8) | NO |
| 55 | `wo_qty_comp` | numeric(19,8) | NO |
| 56 | `wo_qty_rjct` | numeric(19,8) | NO |
| 57 | `wo_line` | varchar(8) | NO |
| 58 | `wo_ord_date` | datetime | NO |
| 59 | `wo_rel_date` | datetime | NO |
| 60 | `wo_due_date` | datetime | NO |
| 61 | `wo_close_by` | varchar(12) | NO |
| 62 | `wo_close_date` | datetime | YES |
| 63 | `wo_status` | varchar(1) | NO |
| 64 | `wo_so_nbr` | varchar(15) | NO |
| 65 | `wo_so_line` | int(10,0) | NO |
| 66 | `wo_fgov_per` | decimal(19,8) | NO |
| 67 | `wo_rmks` | varchar(255) | NO |
| 68 | `wo_other_rmks` | text(2147483647) | YES |
| 69 | `wo_site` | varchar(8) | NO |
| 70 | `wo_wf_staus` | varchar(1) | NO |
| 71 | `wo_prog_code` | varchar(12) | NO |
| 72 | `wo_doc_code` | varchar(12) | NO |
| 73 | `wo_crt_by` | varchar(12) | NO |
| 74 | `wo_crt_date` | datetime | NO |
| 75 | `wo_mod_times` | int(10,0) | NO |
| 76 | `wo_mod_by` | varchar(12) | NO |
| 77 | `wo_mod_date` | datetime | NO |
| 78 | `wo_char1` | varchar(255) | NO |
| 79 | `wo_char2` | varchar(255) | NO |
| 80 | `wo_char3` | varchar(255) | NO |
| 81 | `wo_char4` | varchar(255) | NO |
| 82 | `wo_char5` | varchar(255) | NO |
| 83 | `wo_char6` | varchar(255) | NO |
| 84 | `wo_qty1` | decimal(19,8) | NO |
| 85 | `wo_qty2` | decimal(19,8) | NO |
| 86 | `wo_src` | varchar(2) | NO |
| 87 | `wo_src_nbr` | varchar(15) | NO |
| 88 | `wo_src_lot` | varchar(18) | NO |
| 89 | `wo_sod_conf` | bit | NO |
| 90 | `wo_sod_conf_by` | varchar(12) | NO |
| 91 | `wo_sod_conf_date` | datetime | YES |
| 92 | `wo_close_reason` | varchar(255) | NO |
| 93 | `wo_data_src` | varchar(1) | NO |
| 94 | `wo_data_id` | varchar(255) | NO |
| 95 | `wo_seq` | varchar(15) | NO |
| 96 | `pt_part` | varchar(30) | NO |
| 97 | `pt_desc1` | varchar(255) | NO |
| 98 | `pt_desc2` | varchar(255) | NO |
| 99 | `pt_custom_code` | varchar(50) | NO |
| 100 | `pt_barcode` | varchar(80) | NO |
| 101 | `pt_spec` | varchar(255) | NO |
| 102 | `pt_um` | varchar(4) | NO |
| 103 | `pt_prod_line` | varchar(4) | NO |
| 104 | `pt_added` | datetime | NO |
| 105 | `pt_part_type` | varchar(30) | NO |
| 106 | `pt_group` | varchar(30) | NO |
| 107 | `pt_draw` | varchar(18) | NO |
| 108 | `pt_picture` | varchar(255) | NO |
| 109 | `pt_rev` | varchar(4) | NO |
| 110 | `pt_status` | bit | NO |
| 111 | `pt_gross_weight` | numeric(19,8) | NO |
| 112 | `pt_net_weight` | numeric(19,8) | NO |
| 113 | `pt_case_qty` | numeric(19,8) | NO |
| 114 | `pt_scrp_pct` | decimal(19,8) | NO |
| 115 | `pt_ship_mark` | varchar(255) | NO |
| 116 | `pt_carton_l` | numeric(19,8) | NO |
| 117 | `pt_carton_w` | numeric(19,8) | NO |
| 118 | `pt_carton_h` | numeric(19,8) | NO |
| 119 | `pt_total` | numeric(19,8) | NO |
| 120 | `pt_um_eng` | varchar(4) | NO |
| 121 | `pt_um_eng_m` | decimal(19,8) | NO |
| 122 | `pt_um_eng_d` | decimal(19,8) | NO |
| 123 | `pt_um_pur` | varchar(4) | NO |
| 124 | `pt_um_pur_m` | decimal(19,8) | NO |
| 125 | `pt_um_pur_d` | decimal(19,8) | NO |
| 126 | `pt_um_sl` | varchar(4) | NO |
| 127 | `pt_um_sl_m` | decimal(19,8) | NO |
| 128 | `pt_um_sl_d` | decimal(19,8) | NO |
| 129 | `pt_um_isu` | varchar(4) | NO |
| 130 | `pt_um_isu_m` | decimal(19,8) | NO |
| 131 | `pt_um_isu_d` | decimal(19,8) | NO |
| 132 | `pt_abc` | varchar(1) | NO |
| 133 | `pt_loc` | varchar(8) | NO |
| 134 | `pt_cyc_int` | int(10,0) | NO |
| 135 | `pt_lot_serial` | bit | NO |
| 136 | `pt_lot_grp` | varchar(15) | NO |
| 137 | `pt_keeper` | varchar(12) | NO |
| 138 | `pt_shelf_life` | int(10,0) | NO |
| 139 | `pt_wo_line` | varchar(8) | NO |
| 140 | `pt_plan_ord` | bit | NO |
| 141 | `pt_time_fence` | int(10,0) | NO |
| 142 | `pt_ord_pol` | varchar(4) | NO |
| 143 | `pt_ord_qty` | numeric(19,8) | NO |
| 144 | `pt_ord_per` | int(10,0) | NO |
| 145 | `pt_sfty_stk` | numeric(19,8) | NO |
| 146 | `pt_rop` | numeric(19,8) | NO |
| 147 | `pt_buyer` | varchar(12) | NO |
| 148 | `pt_planner` | varchar(12) | NO |
| 149 | `pt_memo_item` | bit | NO |
| 150 | `pt_max_qty` | numeric(19,8) | NO |
| 151 | `pt_vend` | varchar(8) | NO |
| 152 | `pt_pm_code` | varchar(1) | NO |
| 153 | `pt_mfg_lt` | int(10,0) | NO |
| 154 | `pt_pur_lt` | int(10,0) | NO |
| 155 | `pt_insp_rqd` | bit | NO |
| 156 | `pt_gr_lt` | int(10,0) | NO |
| 157 | `pt_phantom` | bit | NO |
| 158 | `pt_ord_min` | numeric(19,8) | NO |
| 159 | `pt_ord_mult` | numeric(19,8) | NO |
| 160 | `pt_iss_batch` | numeric(19,8) | NO |
| 161 | `pt_roll_iss` | bit | NO |
| 162 | `pt_fgov_per` | decimal(19,8) | NO |
| 163 | `pt_iss_unlimit` | bit | NO |
| 164 | `pt_level` | int(10,0) | NO |
| 165 | `pt_wf_status` | varchar(1) | NO |
| 166 | `pt_crt_by` | varchar(12) | NO |
| 167 | `pt_crt_date` | datetime | NO |
| 168 | `pt_mod_times` | int(10,0) | NO |
| 169 | `pt_mod_by` | varchar(12) | NO |
| 170 | `pt_mod_date` | datetime | NO |
| 171 | `pt_pst` | bit | NO |
| 172 | `pt_pst_by` | varchar(12) | NO |
| 173 | `pt_pst_date` | datetime | YES |
| 174 | `pt_char1` | varchar(255) | NO |
| 175 | `pt_char2` | varchar(255) | NO |
| 176 | `pt_char3` | varchar(255) | NO |
| 177 | `pt_char4` | varchar(255) | NO |
| 178 | `pt_char5` | varchar(255) | NO |
| 179 | `pt_char6` | varchar(255) | NO |
| 180 | `pt_char7` | varchar(255) | NO |
| 181 | `pt_char8` | varchar(255) | NO |
| 182 | `pt_qty1` | decimal(19,8) | NO |
| 183 | `pt_qty2` | decimal(19,8) | NO |
| 184 | `pt_qty3` | decimal(19,8) | NO |
| 185 | `pt_qty4` | decimal(19,8) | NO |
| 186 | `pt_expu_perm` | bit | NO |
| 187 | `pt_exsl_perm` | bit | NO |
| 188 | `pt_loc_pos` | varchar(18) | NO |
| 189 | `pt_eng` | varchar(12) | NO |
| 190 | `pt_custom_name` | varchar(255) | NO |
| 191 | `pt_op` | int(10,0) | NO |
| 192 | `pt_backflush` | varchar(1) | NO |
| 193 | `pt_backflush_s` | varchar(1) | NO |
| 194 | `pt_sch_type` | varchar(30) | NO |
| 195 | `pt_ovr_unmrp` | bit | NO |
| 196 | `ptp3_site` | varchar(8) | YES |
| 197 | `ptp3_part` | varchar(30) | YES |
| 198 | `ptp3_mtl_stdtl` | decimal(19,8) | YES |
| 199 | `ptp3_mtl_stdll` | decimal(19,8) | YES |
| 200 | `ptp3_lbr_stdtl` | decimal(19,8) | YES |
| 201 | `ptp3_lbr_stdll` | decimal(19,8) | YES |
| 202 | `ptp3_bdn_stdtl` | decimal(19,8) | YES |
| 203 | `ptp3_bdn_stdll` | decimal(19,8) | YES |
| 204 | `ptp3_sub_stdtl` | decimal(19,8) | YES |
| 205 | `ptp3_sub_stdll` | decimal(19,8) | YES |
| 206 | `ptp3_crt_by` | varchar(12) | YES |
| 207 | `ptp3_crt_date` | datetime | YES |
| 208 | `ptp3_mod_times` | int(10,0) | YES |
| 209 | `ptp3_mod_by` | varchar(12) | YES |
| 210 | `ptp3_mod_date` | datetime | YES |
| 211 | `ptp3_char1` | varchar(255) | YES |
| 212 | `ptp3_char2` | varchar(255) | YES |
| 213 | `ptp3_char3` | varchar(255) | YES |
| 214 | `ptp3_char4` | varchar(255) | YES |
| 215 | `ptp3_char5` | varchar(255) | YES |
| 216 | `ptp3_char6` | varchar(255) | YES |
| 217 | `ptp3_qty1` | decimal(19,8) | YES |
| 218 | `ptp3_qty2` | decimal(19,8) | YES |
| 219 | `ptp3_min_sod_price` | decimal(19,8) | YES |
| 220 | `ptp3_max_pur_cost` | decimal(19,8) | YES |
| 221 | `tr_nbr` | varchar(15) | YES |
| 222 | `tr_lot` | varchar(18) | YES |
| 223 | `tr_line` | int(10,0) | YES |
| 224 | `tr_qty_loc` | numeric(38,8) | YES |
| 225 | `tr_amt_tot` | decimal(38,8) | YES |

### `dbo.v_wr_op` (VIEW)

| 序号 | 字段 | 类型 | 可空 |
| ---: | --- | --- | --- |
| 1 | `wr_nbr` | varchar(15) | NO |
| 2 | `wr_lot` | varchar(18) | NO |
| 3 | `wr_op` | int(10,0) | NO |
| 4 | `wr_desc` | varchar(100) | NO |
| 5 | `wr_wkctr` | varchar(8) | NO |
| 6 | `wr_qty_ord` | numeric(19,8) | NO |
| 7 | `wr_qty_comp` | numeric(19,8) | NO |
| 8 | `wr_run_act` | numeric(19,8) | NO |
| 9 | `wr_qty_rjct` | numeric(19,8) | NO |
| 10 | `wr_yield_pct` | decimal(19,8) | NO |
| 11 | `wr_tool` | varchar(80) | NO |
| 12 | `wr_param` | varchar(255) | NO |
| 13 | `wr_start` | datetime | NO |
| 14 | `wr_due` | datetime | NO |
| 15 | `wr_run` | numeric(19,8) | NO |
| 16 | `wr_prod_rate` | numeric(19,8) | NO |
| 17 | `wr_um` | varchar(1) | NO |
| 18 | `wr_rmks` | varchar(255) | NO |
| 19 | `wr_crt_by` | varchar(12) | NO |
| 20 | `wr_crt_date` | datetime | NO |
| 21 | `wr_mod_times` | int(10,0) | NO |
| 22 | `wr_mod_by` | varchar(12) | NO |
| 23 | `wr_mod_date` | datetime | NO |
| 24 | `wr_char1` | varchar(255) | NO |
| 25 | `wr_char2` | varchar(255) | NO |
| 26 | `wr_char3` | varchar(255) | NO |
| 27 | `wr_char4` | varchar(255) | NO |
| 28 | `wr_char5` | varchar(255) | NO |
| 29 | `wr_char6` | varchar(255) | NO |
| 30 | `wr_qty1` | decimal(19,8) | NO |
| 31 | `wr_qty2` | decimal(19,8) | NO |
| 32 | `wr_alt` | bit | NO |
| 33 | `wr_alt_op` | int(10,0) | NO |
| 34 | `wr_s_price` | decimal(19,8) | NO |
| 35 | `wr_s_price_vat` | decimal(19,8) | NO |
| 36 | `wr_vend` | varchar(8) | NO |
| 37 | `wr_vat` | numeric(19,8) | NO |
| 38 | `wr_um_rate` | numeric(19,8) | NO |
| 39 | `wr_data_src` | varchar(1) | NO |
| 40 | `wr_data_id` | varchar(255) | NO |
| 41 | `wr_first` | bit | NO |
| 42 | `wr_op_type` | varchar(30) | NO |
| 43 | `wr_equ` | bit | NO |
| 44 | `wr_mou` | bit | NO |
| 45 | `wr_usr` | bit | NO |
| 46 | `wr_part` | varchar(30) | NO |
| 47 | `wr_att` | bit | NO |
| 48 | `wr_devices` | varchar(15) | NO |
| 49 | `wr_type` | varchar(1) | NO |
| 50 | `wr_po_part` | varchar(30) | NO |
| 51 | `wo_nbr` | varchar(15) | NO |
| 52 | `wo_lot` | varchar(18) | NO |
| 53 | `wo_type` | varchar(1) | NO |
| 54 | `wo_type2` | varchar(1) | NO |
| 55 | `wo_part` | varchar(30) | NO |
| 56 | `wo_qty_ord` | numeric(19,8) | NO |
| 57 | `wo_qty_comp` | numeric(19,8) | NO |
| 58 | `wo_qty_rjct` | numeric(19,8) | NO |
| 59 | `wo_line` | varchar(8) | NO |
| 60 | `wo_ord_date` | datetime | NO |
| 61 | `wo_rel_date` | datetime | NO |
| 62 | `wo_due_date` | datetime | NO |
| 63 | `wo_close_by` | varchar(12) | NO |
| 64 | `wo_close_date` | datetime | YES |
| 65 | `wo_status` | varchar(1) | NO |
| 66 | `wo_so_nbr` | varchar(15) | NO |
| 67 | `wo_so_line` | int(10,0) | NO |
| 68 | `wo_fgov_per` | decimal(19,8) | NO |
| 69 | `wo_rmks` | varchar(255) | NO |
| 70 | `wo_other_rmks` | text(2147483647) | YES |
| 71 | `wo_site` | varchar(8) | NO |
| 72 | `wo_wf_staus` | varchar(1) | NO |
| 73 | `wo_prog_code` | varchar(12) | NO |
| 74 | `wo_doc_code` | varchar(12) | NO |
| 75 | `wo_crt_by` | varchar(12) | NO |
| 76 | `wo_crt_date` | datetime | NO |
| 77 | `wo_mod_times` | int(10,0) | NO |
| 78 | `wo_mod_by` | varchar(12) | NO |
| 79 | `wo_mod_date` | datetime | NO |
| 80 | `wo_char1` | varchar(255) | NO |
| 81 | `wo_char2` | varchar(255) | NO |
| 82 | `wo_char3` | varchar(255) | NO |
| 83 | `wo_char4` | varchar(255) | NO |
| 84 | `wo_char5` | varchar(255) | NO |
| 85 | `wo_char6` | varchar(255) | NO |
| 86 | `wo_qty1` | decimal(19,8) | NO |
| 87 | `wo_qty2` | decimal(19,8) | NO |
| 88 | `wo_src` | varchar(2) | NO |
| 89 | `wo_src_nbr` | varchar(15) | NO |
| 90 | `wo_src_lot` | varchar(18) | NO |
| 91 | `wo_sod_conf` | bit | NO |
| 92 | `wo_sod_conf_by` | varchar(12) | NO |
| 93 | `wo_sod_conf_date` | datetime | YES |
| 94 | `wo_close_reason` | varchar(255) | NO |
| 95 | `wo_data_src` | varchar(1) | NO |
| 96 | `wo_data_id` | varchar(255) | NO |
| 97 | `wo_seq` | varchar(15) | NO |
| 98 | `pt_desc1` | varchar(255) | NO |
| 99 | `pt_spec` | varchar(255) | NO |
| 100 | `dpmd_qty_ord` | numeric(38,8) | NO |
| 101 | `un_dpm_qty` | numeric(38,8) | YES |
| 102 | `pfbd_qty_unpst` | numeric(38,8) | NO |
| 103 | `un_pfb_qty` | numeric(38,8) | YES |

## 外键关系

| 源对象.字段 | 目标对象.字段 |
| --- | --- |
| `dbo.ac_mstr.ac_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.acds_det.acds_code` | `dbo.ac_mstr.ac_code` |
| `dbo.acg_mstr.acg_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.acgd_det.acgd_nbr` | `dbo.acg_mstr.acg_nbr` |
| `dbo.acgd_det.acgd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.acgd2_det.acgd2_line` | `dbo.acgd_det.acgd_line` |
| `dbo.acgd2_det.acgd2_nbr` | `dbo.acgd_det.acgd_nbr` |
| `dbo.acgd2_det.acgd2_part` | `dbo.pt_mstr.pt_part` |
| `dbo.adjd_det.adjd_adj` | `dbo.adj_mstr.adj_adj` |
| `dbo.adjd_det.adjd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.adjsd_det.adjsd_adj` | `dbo.adjs_mstr.adjs_adj` |
| `dbo.adjsd_det.adjsd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.adjsd2_det.adjsd2_adj` | `dbo.adjsd_det.adjsd_adj` |
| `dbo.adjsd2_det.adjsd2_line` | `dbo.adjsd_det.adjsd_line` |
| `dbo.adjsd2_det.adjsd2_part` | `dbo.pt_mstr.pt_part` |
| `dbo.aid_det.aid_type` | `dbo.ai_mstr.ai_type` |
| `dbo.ancd_det.ancd_nbr` | `dbo.anc_mstr.anc_nbr` |
| `dbo.ap_mstr.ap_doc_code` | `dbo.vt_mstr.vt_code` |
| `dbo.ap_mstr.ap_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.ap_mstr.ap_vendor` | `dbo.vd_mstr.vd_addr` |
| `dbo.apd_det.apd_nbr` | `dbo.ap_mstr.ap_nbr` |
| `dbo.apn_mstr.apn_doc_code` | `dbo.vt_mstr.vt_code` |
| `dbo.apn_mstr.apn_vendor` | `dbo.vd_mstr.vd_addr` |
| `dbo.apnd_det.apnd_nbr` | `dbo.apn_mstr.apn_nbr` |
| `dbo.ar_mstr.ar_customer` | `dbo.cm_mstr.cm_addr` |
| `dbo.ar_mstr.ar_doc_code` | `dbo.vt_mstr.vt_code` |
| `dbo.ar_mstr.ar_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.ard_det.ard_nbr` | `dbo.ar_mstr.ar_nbr` |
| `dbo.asi_mstr.asi_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.asid_det.asid_ast_code` | `dbo.ast_mstr.ast_code` |
| `dbo.asid_det.asid_nbr` | `dbo.asi_mstr.asi_nbr` |
| `dbo.asid_det.asid_part` | `dbo.pt_mstr.pt_part` |
| `dbo.asid2_det.asid2_line` | `dbo.asid_det.asid_line` |
| `dbo.asid2_det.asid2_nbr` | `dbo.asid_det.asid_nbr` |
| `dbo.asid3_det.asid3_line` | `dbo.asid_det.asid_line` |
| `dbo.asid3_det.asid3_nbr` | `dbo.asid_det.asid_nbr` |
| `dbo.asid3_det.asid3_part` | `dbo.pt_mstr.pt_part` |
| `dbo.aso_mstr.aso_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.asod_det.asod_nbr` | `dbo.aso_mstr.aso_nbr` |
| `dbo.asod_det.asod_part` | `dbo.pt_mstr.pt_part` |
| `dbo.asqd_det.asqd_nbr` | `dbo.asq_mstr.asq_nbr` |
| `dbo.asqd_det.asqd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.asqd_det.asqd_src_line` | `dbo.asid_det.asid_line` |
| `dbo.asqd_det.asqd_src_nbr` | `dbo.asid_det.asid_nbr` |
| `dbo.asqd2_det.asqd2_line` | `dbo.asqd_det.asqd_line` |
| `dbo.asqd2_det.asqd2_nbr` | `dbo.asqd_det.asqd_nbr` |
| `dbo.auto_imp2.tmp_flow` | `dbo.auto_imp.tmp_flow` |
| `dbo.auto_imp2.tmp_user` | `dbo.auto_imp.tmp_user` |
| `dbo.auto_wtf2.aw2_flow` | `dbo.auto_wtf1.aw_flow` |
| `dbo.bgd_det.bgd_nbr` | `dbo.bg_mstr.bg_nbr` |
| `dbo.bom_mstr.bom_parent` | `dbo.pt_mstr.pt_part` |
| `dbo.ca_mstr.ca_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.cajd_det.cajd_nbr` | `dbo.caj_mstr.caj_nbr` |
| `dbo.cajd_det.cajd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.capd_det.capd_code` | `dbo.cap_mstr.cap_code` |
| `dbo.cend_det.cend_nbr` | `dbo.cen_mstr.cen_nbr` |
| `dbo.cf_mstr.cf_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.cfd_det.cfd_nbr` | `dbo.cf_mstr.cf_nbr` |
| `dbo.cfd_det.cfd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.cid_det.cid_code` | `dbo.ci_mstr.ci_code` |
| `dbo.cinv_mstr.cinv_cr_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.cinv_mstr.cinv_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.cinv_mstr.cinv_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.cinv_mstr.cinv_site` | `dbo.si_mstr.si_site` |
| `dbo.cinvd_det.cinvd_nbr` | `dbo.cinv_mstr.cinv_nbr` |
| `dbo.cinvd_det.cinvd_so_line` | `dbo.sod_det.sod_line` |
| `dbo.cinvd_det.cinvd_so_nbr` | `dbo.sod_det.sod_nbr` |
| `dbo.cm_mstr.cm_cr_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.cm_mstr.cm_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.cmds_det.cmds_addr` | `dbo.cm_mstr.cm_addr` |
| `dbo.cp_mstr.cp_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.cp_mstr.cp_part` | `dbo.pt_mstr.pt_part` |
| `dbo.cpds_det.cpds_cust` | `dbo.cp_mstr.cp_cust` |
| `dbo.cpds_det.cpds_cust_part` | `dbo.cp_mstr.cp_cust_part` |
| `dbo.cpds_det.cpds_part` | `dbo.cp_mstr.cp_part` |
| `dbo.cpm_mstr.cpm_customer` | `dbo.cm_mstr.cm_addr` |
| `dbo.cpm_mstr.cpm_doc_code` | `dbo.vt_mstr.vt_code` |
| `dbo.cpmd_det.cpmd_nbr` | `dbo.cpm_mstr.cpm_nbr` |
| `dbo.cr_mstr.cr_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.crd_det.crd_cr` | `dbo.cr_mstr.cr_cr` |
| `dbo.crd_det.crd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.crecd_det.crecd_code` | `dbo.crec_mstr.crec_code` |
| `dbo.cu_mstr.cu_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.dad_det.dad_nbr` | `dbo.da_mstr.da_nbr` |
| `dbo.dn_mstr.dn_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.dna_mstr.dna_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.dna_mstr.dna_site` | `dbo.si_mstr.si_site` |
| `dbo.dnad_det.dnad_nbr` | `dbo.dna_mstr.dna_nbr` |
| `dbo.dnad_det.dnad_part` | `dbo.pt_mstr.pt_part` |
| `dbo.dnad_det.dnad_so` | `dbo.sod_det.sod_nbr` |
| `dbo.dnad_det.dnad_so_line` | `dbo.sod_det.sod_line` |
| `dbo.dnd_det.dnd_dn` | `dbo.dn_mstr.dn_dn` |
| `dbo.dnd_det.dnd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.dnd_det.dnd_so` | `dbo.sod_det.sod_nbr` |
| `dbo.dnd_det.dnd_so_line` | `dbo.sod_det.sod_line` |
| `dbo.dpm_mstr.dpm_site` | `dbo.si_mstr.si_site` |
| `dbo.dpmad_auto.dpmad_user` | `dbo.dpma_auto.dpma_user` |
| `dbo.dpmad_auto.dpmad_wr_lot` | `dbo.dpma_auto.dpma_wr_lot` |
| `dbo.dpmad_auto.dpmad_wr_nbr` | `dbo.dpma_auto.dpma_wr_nbr` |
| `dbo.dpmad_auto.dpmad_wr_op` | `dbo.dpma_auto.dpma_wr_op` |
| `dbo.dpmd_det.dpmd_nbr` | `dbo.dpm_mstr.dpm_nbr` |
| `dbo.dpmd_det.dpmd_wr_lot` | `dbo.wr_route.wr_lot` |
| `dbo.dpmd_det.dpmd_wr_nbr` | `dbo.wr_route.wr_nbr` |
| `dbo.dpmd_det.dpmd_wr_op` | `dbo.wr_route.wr_op` |
| `dbo.ecd1_det.ecd1_comp` | `dbo.pt_mstr.pt_part` |
| `dbo.ecd1_det.ecd1_nbr` | `dbo.ecm_mstr.ecm_nbr` |
| `dbo.ecd1_det.ecd1_par` | `dbo.pt_mstr.pt_part` |
| `dbo.ecd2_det.ecd2_line` | `dbo.ecd1_det.ecd1_line` |
| `dbo.ecd2_det.ecd2_nbr` | `dbo.ecd1_det.ecd1_nbr` |
| `dbo.ecd3_det.ecd3_line` | `dbo.ecd1_det.ecd1_line` |
| `dbo.ecd3_det.ecd3_nbr` | `dbo.ecd1_det.ecd1_nbr` |
| `dbo.exd_det.exd_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.exp_mstr.exp_prog` | `dbo.extp_mstr.extp_code` |
| `dbo.facd_det.facd_fas_code` | `dbo.fas_mstr.fas_code` |
| `dbo.facd_det.facd_nbr` | `dbo.fac_mstr.fac_nbr` |
| `dbo.facdd_det.facdd_line` | `dbo.facd_det.facd_line` |
| `dbo.facdd_det.facdd_nbr` | `dbo.facd_det.facd_nbr` |
| `dbo.far_mstr.far_fas_code` | `dbo.fas_mstr.fas_code` |
| `dbo.fas_mstr.fas_src` | `dbo.fch_mstr.fch_code` |
| `dbo.fas_mstr.fas_status` | `dbo.fst_mstr.fst_code` |
| `dbo.fas_mstr.fas_type` | `dbo.fty_mstr.fty_code` |
| `dbo.fasd_det.fasd_code` | `dbo.fas_mstr.fas_code` |
| `dbo.fcd_det.fcd_nbr` | `dbo.fc_mstr.fc_nbr` |
| `dbo.fcg_mstr.fcg_fas_code` | `dbo.fas_mstr.fas_code` |
| `dbo.fdpd_det.fdpd_fas_code` | `dbo.fas_mstr.fas_code` |
| `dbo.fdpd_det.fdpd_nbr` | `dbo.fdp_mstr.fdp_nbr` |
| `dbo.fdpd2_det.fdpd2_line` | `dbo.fdpd_det.fdpd_line` |
| `dbo.fdpd2_det.fdpd2_nbr` | `dbo.fdpd_det.fdpd_nbr` |
| `dbo.fgrd_det.fgrd_fgr` | `dbo.fgr_mstr.fgr_fgr` |
| `dbo.fgrd_det.fgrd_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.fgrd_det.fgrd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.fgrd_det.fgrd_site` | `dbo.loc_mstr.loc_site` |
| `dbo.fgrd_det.fgrd_wo_lot` | `dbo.wo_mstr.wo_lot` |
| `dbo.fgrd_det.fgrd_wo_nbr` | `dbo.wo_mstr.wo_nbr` |
| `dbo.fgrd1_det.fgrd1_fgr` | `dbo.fgrd_det.fgrd_fgr` |
| `dbo.fgrd1_det.fgrd1_line` | `dbo.fgrd_det.fgrd_line` |
| `dbo.fgrd2_det.fgrd2_fgr` | `dbo.fgrd1_det.fgrd1_fgr` |
| `dbo.fgrd2_det.fgrd2_line` | `dbo.fgrd1_det.fgrd1_line` |
| `dbo.fgrd2_det.fgrd2_seq` | `dbo.fgrd1_det.fgrd1_seq` |
| `dbo.fwmd_det.fwmd_company` | `dbo.fwm_mstr.fwm_company` |
| `dbo.fwmd_det.fwmd_fas_code` | `dbo.fas_mstr.fas_code` |
| `dbo.fwmd_det.fwmd_month` | `dbo.fwm_mstr.fwm_month` |
| `dbo.fwmd_det.fwmd_year` | `dbo.fwm_mstr.fwm_year` |
| `dbo.gend_det.gend_gen` | `dbo.gen_mstr.gen_gen` |
| `dbo.grn_mstr.grn_site` | `dbo.si_mstr.si_site` |
| `dbo.grn_mstr.grn_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.grnd_det.grnd_grn` | `dbo.grn_mstr.grn_grn` |
| `dbo.grnd_det.grnd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.grnd_det.grnd_po` | `dbo.pod_det.pod_nbr` |
| `dbo.grnd_det.grnd_po_line` | `dbo.pod_det.pod_line` |
| `dbo.hremp_mstr.hremp_dept` | `dbo.dp_mstr.dp_code` |
| `dbo.hremp_mstr.hremp_position` | `dbo.hrpo_mstr.hrpo_code` |
| `dbo.hrslyd_det.hrslyd_emp` | `dbo.hremp_mstr.hremp_code` |
| `dbo.hrslyd_det.hrslyd_flow` | `dbo.hrsly_mstr.hrsly_flow` |
| `dbo.hrtr_mstr.hrtr_emp` | `dbo.hremp_mstr.hremp_code` |
| `dbo.impd_det.impd_code` | `dbo.imp_mstr.imp_code` |
| `dbo.impdd_det.impdd_code` | `dbo.impd_det.impd_code` |
| `dbo.impdd_det.impdd_field` | `dbo.impd_det.impd_field` |
| `dbo.impdd_det.impdd_table` | `dbo.impd_det.impd_table` |
| `dbo.impdt_det.impdt_code` | `dbo.impd_det.impd_code` |
| `dbo.impdt_det.impdt_field` | `dbo.impd_det.impd_field` |
| `dbo.impdt_det.impdt_table` | `dbo.impd_det.impd_table` |
| `dbo.inb_hist_202512.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202512.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202512.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202601.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202601.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202601.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202602.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202602.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202602.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202603.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202603.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202603.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202604.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202604.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202604.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202605.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202605.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202605.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202606.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202606.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202606.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202607.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202607.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202607.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202608.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202608.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202608.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_202609.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_202609.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_202609.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inb_hist_org.inb_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.inb_hist_org.inb_part` | `dbo.pt_mstr.pt_part` |
| `dbo.inb_hist_org.inb_site` | `dbo.loc_mstr.loc_site` |
| `dbo.inv_mstr.inv_cr_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.inv_mstr.inv_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.inv_mstr.inv_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.inv_mstr.inv_site` | `dbo.si_mstr.si_site` |
| `dbo.invd_det.invd_nbr` | `dbo.inv_mstr.inv_nbr` |
| `dbo.iqcd_det.iqcd_grn` | `dbo.grnd_det.grnd_grn` |
| `dbo.iqcd_det.iqcd_grn_line` | `dbo.grnd_det.grnd_line` |
| `dbo.iqcd_det.iqcd_iqc` | `dbo.iqc_mstr.iqc_iqc` |
| `dbo.iqcd_det.iqcd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.iqcd1_det.iqcd1_iqc` | `dbo.iqcd_det.iqcd_iqc` |
| `dbo.iqcd1_det.iqcd1_line` | `dbo.iqcd_det.iqcd_line` |
| `dbo.iqcd2_det.iqcd2_iqc` | `dbo.iqcd1_det.iqcd1_iqc` |
| `dbo.iqcd2_det.iqcd2_line` | `dbo.iqcd1_det.iqcd1_line` |
| `dbo.iqcd2_det.iqcd2_seq` | `dbo.iqcd1_det.iqcd1_seq` |
| `dbo.ld_det.ld_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.ld_det.ld_part` | `dbo.pt_mstr.pt_part` |
| `dbo.ld_det.ld_site` | `dbo.loc_mstr.loc_site` |
| `dbo.ldp_det.ldp_loc` | `dbo.ld_det.ld_loc` |
| `dbo.ldp_det.ldp_lot` | `dbo.ld_det.ld_lot` |
| `dbo.ldp_det.ldp_part` | `dbo.ld_det.ld_part` |
| `dbo.ldp_det.ldp_site` | `dbo.ld_det.ld_site` |
| `dbo.ln_mstr.ln_loc_ovr` | `dbo.loc_mstr.loc_loc` |
| `dbo.ln_mstr.ln_site` | `dbo.loc_mstr.loc_site` |
| `dbo.loc_mstr.loc_site` | `dbo.si_mstr.si_site` |
| `dbo.lpd_det.lpd_nbr` | `dbo.lp_mstr.lp_nbr` |
| `dbo.lpd_det.lpd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.lpd2_det.lpd2_date` | `dbo.lpd_det.lpd_date` |
| `dbo.lpd2_det.lpd2_line` | `dbo.lpd_det.lpd_line` |
| `dbo.lpd2_det.lpd2_nbr` | `dbo.lpd_det.lpd_nbr` |
| `dbo.movd_det.movd_mov` | `dbo.mov_mstr.mov_mov` |
| `dbo.movd_det.movd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.mrp_det.mrp_part` | `dbo.pt_mstr.pt_part` |
| `dbo.mrp_det.mrp_site` | `dbo.si_mstr.si_site` |
| `dbo.mtr_mstr.mtr_site` | `dbo.si_mstr.si_site` |
| `dbo.mtrd_det.mtrd_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.mtrd_det.mtrd_mtr` | `dbo.mtr_mstr.mtr_mtr` |
| `dbo.mtrd_det.mtrd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.mtrd_det.mtrd_site` | `dbo.loc_mstr.loc_site` |
| `dbo.mtrd_det.mtrd_wo_lot` | `dbo.wo_mstr.wo_lot` |
| `dbo.mtrd_det.mtrd_wo_nbr` | `dbo.wo_mstr.wo_nbr` |
| `dbo.mts_mstr.mts_site` | `dbo.si_mstr.si_site` |
| `dbo.mtsd_det.mtsd_mts` | `dbo.mts_mstr.mts_mts` |
| `dbo.mtsd_det.mtsd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.mtsd_det.mtsd_seq` | `dbo.wod_det.wod_seq` |
| `dbo.mtsd_det.mtsd_wo_lot` | `dbo.wod_det.wod_lot` |
| `dbo.mtsd_det.mtsd_wo_nbr` | `dbo.wod_det.wod_nbr` |
| `dbo.oa_det.oa_part` | `dbo.pt_mstr.pt_part` |
| `dbo.oa_det.oa_site` | `dbo.si_mstr.si_site` |
| `dbo.opd_det.opd_ac_code` | `dbo.ac_mstr.ac_code` |
| `dbo.opd_det.opd_company` | `dbo.op_mstr.op_company` |
| `dbo.opd2_det.opd2_company` | `dbo.opd_det.opd_company` |
| `dbo.opd2_det.opd2_line` | `dbo.opd_det.opd_line` |
| `dbo.pack_mstr.pack_cinv_nbr` | `dbo.cinv_mstr.cinv_nbr` |
| `dbo.pack_mstr.pack_site` | `dbo.si_mstr.si_site` |
| `dbo.packd_det.packd_cinv_line` | `dbo.cinvd_det.cinvd_line` |
| `dbo.packd_det.packd_cinv_nbr` | `dbo.cinvd_det.cinvd_nbr` |
| `dbo.packd_det.packd_nbr` | `dbo.pack_mstr.pack_nbr` |
| `dbo.pc_mstr.pc_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.pc_mstr.pc_part` | `dbo.pt_mstr.pt_part` |
| `dbo.pc_mstr.pc_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.pcd_det.pcd_nbr` | `dbo.pc_mstr.pc_nbr` |
| `dbo.pcrd_det.pcrd_code` | `dbo.pcr_mstr.pcr_code` |
| `dbo.pcrd2_det.pcrd2_code` | `dbo.pcrd_det.pcrd_code` |
| `dbo.pcrd2_det.pcrd2_line` | `dbo.pcrd_det.pcrd_line` |
| `dbo.pfb_mstr.pfb_site` | `dbo.si_mstr.si_site` |
| `dbo.pfbd_det.pfbd_pfb` | `dbo.pfb_mstr.pfb_pfb` |
| `dbo.pfbd2_det.pfbd2_line` | `dbo.pfbd_det.pfbd_line` |
| `dbo.pfbd2_det.pfbd2_pfb` | `dbo.pfbd_det.pfbd_pfb` |
| `dbo.pk_mstr.pk_site` | `dbo.si_mstr.si_site` |
| `dbo.pkd_det.pkd_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.pkd_det.pkd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.pkd_det.pkd_pk` | `dbo.pk_mstr.pk_pk` |
| `dbo.pkd_det.pkd_site` | `dbo.loc_mstr.loc_site` |
| `dbo.pkd_det.pkd_wo_lot` | `dbo.wo_mstr.wo_lot` |
| `dbo.pkd_det.pkd_wo_nbr` | `dbo.wo_mstr.wo_nbr` |
| `dbo.pla_mstr.pla_pg_nbr` | `dbo.pg_mstr.pg_nbr` |
| `dbo.plad_det.plad_nbr` | `dbo.pla_mstr.pla_nbr` |
| `dbo.pm_mstr.pm_doc_code` | `dbo.vt_mstr.vt_code` |
| `dbo.pm_mstr.pm_vendor` | `dbo.vd_mstr.vd_addr` |
| `dbo.pmad_det.pmad_nbr` | `dbo.pma_mstr.pma_nbr` |
| `dbo.pmad1_det.pmad1_line` | `dbo.pmad_det.pmad_line` |
| `dbo.pmad1_det.pmad1_nbr` | `dbo.pmad_det.pmad_nbr` |
| `dbo.pmd_det.pmd_nbr` | `dbo.pm_mstr.pm_nbr` |
| `dbo.po_mstr.po_cr_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.po_mstr.po_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.po_mstr.po_site` | `dbo.si_mstr.si_site` |
| `dbo.po_mstr.po_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.pod_det.pod_nbr` | `dbo.po_mstr.po_nbr` |
| `dbo.pod_det.pod_part` | `dbo.pt_mstr.pt_part` |
| `dbo.podd_det.podd_line` | `dbo.pod_det.pod_line` |
| `dbo.podd_det.podd_nbr` | `dbo.pod_det.pod_nbr` |
| `dbo.podr_det.podr_line` | `dbo.pod_det.pod_line` |
| `dbo.podr_det.podr_nbr` | `dbo.pod_det.pod_nbr` |
| `dbo.pom_mstr.pom_site` | `dbo.si_mstr.si_site` |
| `dbo.pomd_det.pomd_po_nbr` | `dbo.pom_mstr.pom_po_nbr` |
| `dbo.pomd_det.pomd_po_rev` | `dbo.pom_mstr.pom_po_rev` |
| `dbo.pomdd_det.pomdd_line` | `dbo.pomd_det.pomd_line` |
| `dbo.pomdd_det.pomdd_po_nbr` | `dbo.pomd_det.pomd_po_nbr` |
| `dbo.pomdd_det.pomdd_po_rev` | `dbo.pomd_det.pomd_po_rev` |
| `dbo.prh_hist.prh_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.prh_hist.prh_part` | `dbo.pt_mstr.pt_part` |
| `dbo.prh_hist.prh_site` | `dbo.si_mstr.si_site` |
| `dbo.prh_hist.prh_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.prod_det.prod_nbr` | `dbo.pro_mstr.pro_nbr` |
| `dbo.prod_det.prod_plad_line` | `dbo.plad_det.plad_line` |
| `dbo.prod_det.prod_plad_nbr` | `dbo.plad_det.plad_nbr` |
| `dbo.ps_mstr.ps_comp` | `dbo.pt_mstr.pt_part` |
| `dbo.ps_mstr.ps_par` | `dbo.bom_mstr.bom_parent` |
| `dbo.psd_det.psd_comp` | `dbo.ps_mstr.ps_comp` |
| `dbo.psd_det.psd_par` | `dbo.ps_mstr.ps_par` |
| `dbo.psd_det.psd_start` | `dbo.ps_mstr.ps_start` |
| `dbo.psdc_det.psdc_comp` | `dbo.ps_mstr.ps_comp` |
| `dbo.psdc_det.psdc_par` | `dbo.ps_mstr.ps_par` |
| `dbo.psdc_det.psdc_start` | `dbo.ps_mstr.ps_start` |
| `dbo.psvd_det.psvd_par` | `dbo.psve_det.psve_par` |
| `dbo.psvd_det.psvd_version` | `dbo.psve_det.psve_version` |
| `dbo.psve_det.psve_par` | `dbo.bom_mstr.bom_parent` |
| `dbo.pt_mstr.pt_prod_line` | `dbo.pl_mstr.pl_prod_line` |
| `dbo.ptds_det.ptds_part` | `dbo.pt_mstr.pt_part` |
| `dbo.ptp1_det.ptp1_part` | `dbo.pt_mstr.pt_part` |
| `dbo.ptp1_det.ptp1_site` | `dbo.si_mstr.si_site` |
| `dbo.ptp2_det.ptp2_part` | `dbo.pt_mstr.pt_part` |
| `dbo.ptp2_det.ptp2_site` | `dbo.si_mstr.si_site` |
| `dbo.ptp3_det.ptp3_part` | `dbo.pt_mstr.pt_part` |
| `dbo.ptp3_det.ptp3_site` | `dbo.si_mstr.si_site` |
| `dbo.ptp3a_det.ptp3a_part` | `dbo.ptp3_det.ptp3_part` |
| `dbo.ptp3a_det.ptp3a_site` | `dbo.ptp3_det.ptp3_site` |
| `dbo.ptp3b_det.ptp3b_part` | `dbo.ptp3a_det.ptp3a_part` |
| `dbo.ptp3b_det.ptp3b_site` | `dbo.ptp3a_det.ptp3a_site` |
| `dbo.ptp3b_det.ptp3b_start` | `dbo.ptp3a_det.ptp3a_start` |
| `dbo.ptp3c_det.ptp3c_part` | `dbo.ptp3_det.ptp3_part` |
| `dbo.ptp3c_det.ptp3c_site` | `dbo.ptp3_det.ptp3_site` |
| `dbo.ptp3d_det.ptp3d_part` | `dbo.ptp3c_det.ptp3c_part` |
| `dbo.ptp3d_det.ptp3d_site` | `dbo.ptp3c_det.ptp3c_site` |
| `dbo.ptp3d_det.ptp3d_start` | `dbo.ptp3c_det.ptp3c_start` |
| `dbo.pts_det.pts_part` | `dbo.pt_mstr.pt_part` |
| `dbo.pts_det.pts_sub_part` | `dbo.pt_mstr.pt_part` |
| `dbo.ptssd_det.ptssd_nbr` | `dbo.ptss_mstr.ptss_nbr` |
| `dbo.qexd_det.qexd_nbr` | `dbo.qex_mstr.qex_nbr` |
| `dbo.qexq_det.qexq_nbr` | `dbo.qex_mstr.qex_nbr` |
| `dbo.qexv_det.qexv_nbr` | `dbo.qex_mstr.qex_nbr` |
| `dbo.qtd_det.qtd_code` | `dbo.qt_mstr.qt_code` |
| `dbo.QueueData.Queued_ID` | `dbo.QueueMeta.Queue_ID` |
| `dbo.QueueData_SCM.Queued_ID` | `dbo.QueueMeta_SCM.Queue_ID` |
| `dbo.req_mstr.req_part` | `dbo.pt_mstr.pt_part` |
| `dbo.req_mstr.req_pr_nbr` | `dbo.pr_mstr.pr_nbr` |
| `dbo.reqd_det.reqd_pr_nbr` | `dbo.req_mstr.req_pr_nbr` |
| `dbo.reqd_det.reqd_req_line` | `dbo.req_mstr.req_line` |
| `dbo.ro_det.ro_routing` | `dbo.route_mstr.route_routing` |
| `dbo.route_mstr.route_routing` | `dbo.pt_mstr.pt_part` |
| `dbo.rts_mstr.rts_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.rtsd_det.rtsd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.rtsd_det.rtsd_rts` | `dbo.rts_mstr.rts_rts` |
| `dbo.rtsdd_det.rtsdd_line` | `dbo.rtsd_det.rtsd_line` |
| `dbo.rtsdd_det.rtsdd_rts` | `dbo.rtsd_det.rtsd_rts` |
| `dbo.sc_mstr.sc_part` | `dbo.pt_mstr.pt_part` |
| `dbo.scd_det.scd_nbr` | `dbo.sc_mstr.sc_nbr` |
| `dbo.sdh_hist.sdh_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.sdh_hist.sdh_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.sdh_hist.sdh_part` | `dbo.pt_mstr.pt_part` |
| `dbo.sdh_hist.sdh_site` | `dbo.si_mstr.si_site` |
| `dbo.shop_cal.shop_site` | `dbo.si_mstr.si_site` |
| `dbo.so_mstr.so_cr_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.so_mstr.so_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.so_mstr.so_cust` | `dbo.cm_mstr.cm_addr` |
| `dbo.so_mstr.so_site` | `dbo.si_mstr.si_site` |
| `dbo.sod_det.sod_part` | `dbo.pt_mstr.pt_part` |
| `dbo.sodb_det.sodb_line` | `dbo.sod_det.sod_line` |
| `dbo.sodb_det.sodb_nbr` | `dbo.sod_det.sod_nbr` |
| `dbo.sodd_det.sodd_line` | `dbo.sod_det.sod_line` |
| `dbo.sodd_det.sodd_nbr` | `dbo.sod_det.sod_nbr` |
| `dbo.sodpo_det.sodpo_line` | `dbo.sod_det.sod_line` |
| `dbo.sodpo_det.sodpo_nbr` | `dbo.sod_det.sod_nbr` |
| `dbo.sodr_det.sodr_line` | `dbo.sod_det.sod_line` |
| `dbo.sodr_det.sodr_nbr` | `dbo.sod_det.sod_nbr` |
| `dbo.som_mstr.som_site` | `dbo.si_mstr.si_site` |
| `dbo.somd_det.somd_so_nbr` | `dbo.som_mstr.som_so_nbr` |
| `dbo.somd_det.somd_so_rev` | `dbo.som_mstr.som_so_rev` |
| `dbo.tpt_vchd2_det.tpt_vchd2_line` | `dbo.tpt_vchd_det.tpt_vchd_line` |
| `dbo.tpt_vchd2_det.tpt_vchd2_src_nbr` | `dbo.tpt_vchd_det.tpt_vchd_src_nbr` |
| `dbo.tpt_vchd2_det.tpt_vchd2_src_prog` | `dbo.tpt_vchd_det.tpt_vchd_src_prog` |
| `dbo.tpt_vchd2_det.tpt_vchd2_user` | `dbo.tpt_vchd_det.tpt_vchd_user` |
| `dbo.tr_hist.tr_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.tr_hist.tr_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.tr_hist.tr_part` | `dbo.pt_mstr.pt_part` |
| `dbo.tr_hist.tr_site` | `dbo.loc_mstr.loc_site` |
| `dbo.tr_hist_rec.tr_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.tr_hist_rec.tr_loc` | `dbo.loc_mstr.loc_loc` |
| `dbo.tr_hist_rec.tr_part` | `dbo.pt_mstr.pt_part` |
| `dbo.tr_hist_rec.tr_site` | `dbo.loc_mstr.loc_site` |
| `dbo.tsfd_det.tsfd_tsf` | `dbo.tsf_mstr.tsf_tsf` |
| `dbo.tsfd_det.tsfd_wo_lot_iss` | `dbo.wod_det.wod_lot` |
| `dbo.tsfd_det.tsfd_wo_lot_rtn` | `dbo.wo_mstr.wo_lot` |
| `dbo.tsfd_det.tsfd_wo_nbr_iss` | `dbo.wod_det.wod_nbr` |
| `dbo.tsfd_det.tsfd_wo_nbr_rtn` | `dbo.wo_mstr.wo_nbr` |
| `dbo.tsfd_det.tsfd_wo_seq_iss` | `dbo.wod_det.wod_seq` |
| `dbo.udqd_det.udqd_id` | `dbo.udq_mstr.udq_id` |
| `dbo.udqd1_det.udqd1_id` | `dbo.udq_mstr.udq_id` |
| `dbo.usrp_det.usrp_user` | `dbo.usr_mstr.usr_user` |
| `dbo.vchd_det.vchd_ac_code` | `dbo.ac_mstr.ac_code` |
| `dbo.vchd1_det.vchd1_nbr` | `dbo.vch_mstr.vch_nbr` |
| `dbo.vd_mstr.vd_cr_terms` | `dbo.ct_mstr.ct_code` |
| `dbo.vd_mstr.vd_curr` | `dbo.ex_mstr.ex_curr` |
| `dbo.vdad_det.vdad_nbr` | `dbo.vda_mstr.vda_nbr` |
| `dbo.vdad_det.vdad_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.vdd_det.vdd_addr` | `dbo.vd_mstr.vd_addr` |
| `dbo.vdds_det.vdds_addr` | `dbo.vd_mstr.vd_addr` |
| `dbo.vp_mstr.vp_part` | `dbo.pt_mstr.pt_part` |
| `dbo.vp_mstr.vp_vend` | `dbo.vd_mstr.vd_addr` |
| `dbo.vq_mstr.vq_part` | `dbo.pt_mstr.pt_part` |
| `dbo.vq_mstr.vq_site` | `dbo.si_mstr.si_site` |
| `dbo.wc_mstr.wc_dept` | `dbo.dp_mstr.dp_code` |
| `dbo.wfd_det.wfd_doc_type` | `dbo.wf_mstr.wf_doc_type` |
| `dbo.wfd_det.wfd_prog` | `dbo.wf_mstr.wf_prog` |
| `dbo.wfpd_det.wfpd_flow_no` | `dbo.wfp_mstr.wfp_flow_no` |
| `dbo.wo_mstr.wo_part` | `dbo.pt_mstr.pt_part` |
| `dbo.wo_mstr.wo_site` | `dbo.si_mstr.si_site` |
| `dbo.woadjd_det.woadjd_nbr` | `dbo.woadj_mstr.woadj_nbr` |
| `dbo.woadjd_det.woadjd_part` | `dbo.pt_mstr.pt_part` |
| `dbo.wod_det.wod_lot` | `dbo.wo_mstr.wo_lot` |
| `dbo.wod_det.wod_nbr` | `dbo.wo_mstr.wo_nbr` |
| `dbo.wod_det.wod_part` | `dbo.pt_mstr.pt_part` |
| `dbo.womd_det.womd_month` | `dbo.wom_mstr.wom_month` |
| `dbo.womd_det.womd_wod_lot` | `dbo.wom_mstr.wom_wo_lot` |
| `dbo.womd_det.womd_wod_nbr` | `dbo.wom_mstr.wom_wo_nbr` |
| `dbo.womd_det.womd_year` | `dbo.wom_mstr.wom_year` |
| `dbo.wr_route.wr_lot` | `dbo.wo_mstr.wo_lot` |
| `dbo.wr_route.wr_nbr` | `dbo.wo_mstr.wo_nbr` |
| `dbo.wtfd_det.wtfd_nbr` | `dbo.wtf_mstr.wtf_nbr` |
| `dbo.wtfd_det.wtfd_wo_lot_iss` | `dbo.wod_det.wod_lot` |
| `dbo.wtfd_det.wtfd_wo_lot_rtn` | `dbo.wod_det.wod_lot` |
| `dbo.wtfd_det.wtfd_wo_nbr_iss` | `dbo.wod_det.wod_nbr` |
| `dbo.wtfd_det.wtfd_wo_nbr_rtn` | `dbo.wod_det.wod_nbr` |
| `dbo.wtfd_det.wtfd_wo_seq_iss` | `dbo.wod_det.wod_seq` |
| `dbo.wtfd_det.wtfd_wo_seq_rtn` | `dbo.wod_det.wod_seq` |
