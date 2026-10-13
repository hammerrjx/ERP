-- Contributions follow ICLDIQ01_qry. Stock detail includes non-nettable locations.
DECLARE @site varchar(8) = ?;
WITH picked AS (
 SELECT pkd_wo_nbr,pkd_wo_lot,pkd_seq,pkd_part,wod_qty_alloc,
 CASE WHEN SUM(pkd_qty_iss)<wod_qty_alloc THEN SUM(pkd_qty_iss) ELSE wod_qty_alloc END AS qty
 FROM pkd_det JOIN wod_det ON wod_nbr=pkd_wo_nbr AND wod_lot=pkd_wo_lot AND wod_seq=pkd_seq
 JOIN pk_mstr ON pk_pk=pkd_pk
 WHERE EXISTS(SELECT 1 FROM woc_ctrl WHERE woc_pk_mode='2') AND pk_site=@site AND pk_pst=0 AND pkd_type='ISS'
 GROUP BY pkd_wo_nbr,pkd_wo_lot,pkd_seq,pkd_part,wod_qty_alloc
)
SELECT 'stock' AS tab,ld_part AS part,'库存' AS kind,ld_loc AS document,'' AS line,
 ld_loc AS location,loc_desc AS location_name,ld_lot AS lot,pt_loc_pos AS position,
 loc_nettable AS nettable,loc_type AS location_type,ld_qty_oh AS quantity
FROM ld_det JOIN loc_mstr ON loc_site=ld_site AND loc_loc=ld_loc JOIN pt_mstr ON pt_part=ld_part WHERE ld_site=@site
UNION ALL
SELECT 'demand',sod_part,'销售订单',sod_nbr,CAST(sod_line AS varchar(30)),'','','','',0,'',
 (sod_qty_ord+sod_qty_spare-sod_qty_shp-sod_qty_spare_shp)*sod_um_rate_m/sod_um_rate_d
FROM sod_det JOIN so_mstr ON so_nbr=sod_nbr JOIN cm_mstr ON cm_addr=so_cust
WHERE so_site=@site AND sod_status='' AND (cm_consignment=0 OR so_consignment=1) AND so_pst<>0
UNION ALL
SELECT 'demand',fcd_part,'预测',fcd_nbr,'','','','','',0,'',(fcd_qty_fcs-fcd_qty_con)*fcd_um_rate_m/fcd_um_rate_d
FROM fcd_det JOIN fc_mstr ON fc_nbr=fcd_nbr WHERE fc_site=@site AND fcd_closed=0 AND fc_pst<>0
UNION ALL
SELECT 'demand',wod_part,'生产需求',wod_nbr,CAST(wod_seq AS varchar(30)),'','',wod_lot,'',0,'',
 (wod_qty_req+wod_qty_rtnv+wod_qty_rtng-wod_qty_iss-wod_qty_adj)*pt_um_isu_d/pt_um_isu_m
FROM wod_det JOIN wo_mstr ON wo_nbr=wod_nbr AND wo_lot=wod_lot JOIN pt_mstr ON pt_part=wod_part
WHERE wo_site=@site AND wo_status IN ('F','R','A')
UNION ALL
SELECT 'order',pod_part,'采购订单',pod_nbr,CAST(pod_line AS varchar(30)),'','','','',0,'',
 (pod_qty_ord-pod_qty_rcvd+CASE WHEN pod_qty_spare-pod_qty_spare_rcvd>0 THEN pod_qty_spare-pod_qty_spare_rcvd ELSE 0 END)*pod_um_rate_m/pod_um_rate_d
FROM pod_det JOIN po_mstr ON po_nbr=pod_nbr WHERE po_site=@site AND pod_status=''
UNION ALL
SELECT 'order',wo_part,'生产单',wo_nbr,'','','',wo_lot,'',0,'',ISNULL(wo_qty_ord-wo_qty_comp-wo_qty_rjct,0)
FROM wo_mstr WHERE wo_site=@site AND wo_status IN ('F','R','A') AND wo_type2=''
UNION ALL
SELECT 'requisition',req_part,'请购单',req_pr_nbr,'','','','','',0,'',req_qty-req_qty_applied
FROM req_mstr JOIN pr_mstr ON pr_nbr=req_pr_nbr WHERE pr_site=@site AND RTRIM(req_status)=''
UNION ALL
SELECT 'allocation',wod_part,'生产分配',wod_nbr,CAST(wod_seq AS varchar(30)),'','',wod_lot,'',0,'',
 wod_det.wod_qty_alloc-ISNULL(qty,0)*pt_um_isu_d/pt_um_isu_m
FROM wod_det JOIN wo_mstr ON wo_nbr=wod_nbr AND wo_lot=wod_lot JOIN pt_mstr ON pt_part=wod_part
LEFT JOIN picked ON wod_nbr=pkd_wo_nbr AND wod_lot=pkd_wo_lot AND wod_seq=pkd_seq
WHERE wo_site=@site AND wo_status IN ('F','R','A')
UNION ALL
SELECT 'allocation',sod_part,'销售分配',sod_nbr,CAST(sod_line AS varchar(30)),'','','','',0,'',sod_qty_alloc*sod_um_rate_m/sod_um_rate_d
FROM sod_det JOIN so_mstr ON so_nbr=sod_nbr JOIN cm_mstr ON cm_addr=so_cust
WHERE so_site=@site AND sod_status='' AND (cm_consignment=0 OR so_consignment=1)
UNION ALL
SELECT 'allocation',dnd_part,'未审核送货',dnd_dn,'',dnd_loc,loc_desc,'','',loc_nettable,loc_type,
 (dnd_qty_ship+dnd_qty_spare_ship)*dnd_um_rate_m/dnd_um_rate_d
FROM dn_mstr JOIN dnd_det ON dn_dn=dnd_dn JOIN loc_mstr ON loc_site=dn_site AND loc_loc=dnd_loc
JOIN so_mstr ON so_nbr=dnd_so JOIN cm_mstr ON cm_addr=so_cust
WHERE dn_site=@site AND dn_pst=0 AND loc_nettable=1 AND (cm_consignment=0 OR so_consignment=1)
AND NOT EXISTS(SELECT 1 FROM sod_det WHERE sod_nbr=dnd_so AND sod_line=dnd_so_line AND sod_qty_alloc>0 AND sod_status='')
UNION ALL
SELECT 'allocation',movd_part,'未审核计划外出库',movd_mov,'',movd_fr,loc_desc,'','',loc_nettable,loc_type,movd_qty
FROM mov_mstr JOIN movd_det ON mov_mov=movd_mov JOIN loc_mstr ON loc_site=movd_site AND loc_loc=movd_fr
WHERE movd_site=@site AND mov_type='ISS' AND mov_pst=0 AND loc_nettable=1
UNION ALL
SELECT 'allocation',movd_part,'未审核转仓',movd_mov,'',movd_fr,lfr.loc_desc,'','',lfr.loc_nettable,lfr.loc_type,movd_qty
FROM mov_mstr JOIN movd_det ON mov_mov=movd_mov
JOIN loc_mstr lfr ON lfr.loc_site=movd_site AND lfr.loc_loc=movd_fr
JOIN loc_mstr lto ON lto.loc_site=movd_site2 AND lto.loc_loc=movd_to
WHERE movd_site=@site AND mov_type='TR' AND mov_pst=0 AND lfr.loc_nettable=1
AND ((movd_site=movd_site2 AND lto.loc_nettable=0) OR movd_site<>movd_site2)
UNION ALL
SELECT 'allocation',pkd_part,'未审核领料',pkd_pk,'',pkd_loc,loc_desc,'','',loc_nettable,loc_type,pkd_qty_iss*pt_um_isu_d/pt_um_isu_m
FROM pk_mstr JOIN pkd_det ON pk_pk=pkd_pk JOIN loc_mstr ON loc_site=pkd_site AND loc_loc=pkd_loc JOIN pt_mstr ON pt_part=pkd_part
WHERE pk_site=@site AND pk_pst=0 AND loc_nettable=1 AND pkd_type='ISS';
