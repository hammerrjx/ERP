-- ICLDIQ01_qry, verified against local coerp_xgyzx 2026-09-17.
-- Only session temp table writes; business tables are SELECT only.
DECLARE @site varchar(8) = ?, @pt_part_fr varchar(30) = '', @pt_part_to varchar(30) = 'ZZZZZZ', @user varchar(15) = '', @desc_like varchar(255) = '';
    set nocount on

    create table #tmp (
    tmp_part            t_item PRIMARY KEY,
    tmp_qty_oh			t_qty,
    tmp_qty_req_total   t_qty,
    tmp_qty_on_order    t_qty,
    tmp_qty_req_open    t_qty,
    tmp_sfty_stk        t_qty,
    tmp_qty_remain      t_qty,
    tmp_qty_alloc       t_qty,
    tmp_qty_unalloc     t_qty
    )

    select  @site       = isnull(@site, ''),
            @pt_part_fr = isnull(@pt_part_fr, ''),
            @pt_part_to = isnull(@pt_part_to, 'ZZZZZZ')

    if @site = '' or (@pt_part_fr = '' and @pt_part_to = '')
    begin
        select * from #tmp
        return
    end

    insert into #tmp(tmp_part, tmp_qty_oh)
    select pt_part, isnull(sum((case when loc_nettable = 1 then ld_qty_oh else 0 end)), 0)
    from pt_mstr  left join ld_det  on ld_part = pt_part
                              left join loc_mstr  on ld_loc = loc_loc and ld_site = loc_site
    where isnull(ld_site, @site) = @site
      and pt_part between @pt_part_fr and @pt_part_to
      and pt_memo_item = 0
      and (@desc_like = '' or pt_desc1 like '%' + ltrim(rtrim(@desc_like)) + '%' or pt_spec like '%' + ltrim(rtrim(@desc_like)) + '%')
      and (@user = '' or exists(select * from com_sel
                                where com_user = @user and com_prog_code = 'ICLDIQA1' and com_nbr = pt_part))
    group by pt_part

    --订购中
    --采购中
    update #tmp set tmp_qty_on_order = isnull(A.pod_qty, 0)
    from (
          select pod_part, sum((pod_qty_ord - pod_qty_rcvd + (case when pod_qty_spare - pod_qty_spare_rcvd > 0
                                                              then pod_qty_spare - pod_qty_spare_rcvd
                                                              else 0 end)) * pod_um_rate_m / pod_um_rate_d) as pod_qty
          from  pod_det  join #tmp on pod_part = tmp_part
                        join po_mstr  on po_nbr = pod_nbr
          where po_site = @site
            and pod_status = ''
          group by pod_part
         ) A
    where tmp_part = A.pod_part
    --生产中
    update #tmp set tmp_qty_on_order = tmp_qty_on_order + isnull(B.wo_qty, 0)
    from (
          select wo_part, sum(isnull((wo_qty_ord - wo_qty_comp - wo_qty_rjct),0)) as wo_qty
          from  wo_mstr  join #tmp on wo_part = tmp_part
          where wo_status in ('F','R','A')
            and wo_type2 = ''
            and wo_site = @site
          group by wo_part
         ) B
    where tmp_part = B.wo_part

    --总需求
    --客户订单需求
    update #tmp set tmp_qty_req_total = isnull(A.sod_qty, 0)
    from (
          select sod_part, sum((sod_qty_ord + sod_qty_spare - sod_qty_shp - sod_qty_spare_shp) * sod_um_rate_m / sod_um_rate_d) as sod_qty
          from  sod_det  join #tmp on sod_part = tmp_part
                        join so_mstr  on so_nbr = sod_nbr
                        join cm_mstr  on cm_addr = so_cust
          where so_site = @site
            and sod_status = ''
            and (cm_consignment = 0 or so_consignment = 1)
            and so_pst <> 0
          group by sod_part
         ) A
    where tmp_part = A.sod_part
    --预测需求
    update #tmp set tmp_qty_req_total = tmp_qty_req_total + isnull(B.fcd_qty, 0)
    from (
          select fcd_part, sum((fcd_qty_fcs - fcd_qty_con) * fcd_um_rate_m / fcd_um_rate_d) as fcd_qty
          from  fcd_det  join #tmp on fcd_part = tmp_part
                        join fc_mstr  on fc_nbr = fcd_nbr
          where fc_site = @site
            and fcd_closed = 0
            and fc_pst <> 0
          group by fcd_part
         ) B
    where tmp_part = B.fcd_part
    --生产单物料清单需求
    update #tmp set tmp_qty_req_total = tmp_qty_req_total + isnull(C.wod_qty, 0)
    from (
		  select wod_part, sum((wod_qty_req + wod_qty_rtnv + wod_qty_rtng - wod_qty_iss - wod_qty_adj) * pt_um_isu_d / pt_um_isu_m) as wod_qty
          from  wod_det  join #tmp on tmp_part = wod_part
                        join wo_mstr  on wo_nbr = wod_nbr and wo_lot = wod_lot
                        join pt_mstr  on pt_part = tmp_part
          where wo_site = @site
            and wo_status in ('F','R','A')
          group by wod_part
         ) C
    where tmp_part = C.wod_part

    --请购中
    update #tmp set tmp_qty_req_open  = isnull(req_qty, 0)
    from (
          select req_part, sum(req_qty - req_qty_applied) as req_qty
          from  req_mstr  join #tmp on tmp_part = req_part
                         join pr_mstr  on pr_nbr = req_pr_nbr
          where Rtrim(req_status) = ''
            and req_part between @pt_part_fr and @pt_part_to
            and pr_site = @site
          group by req_part
         ) A
    where tmp_part = A.req_part

    --安全库存
    update #tmp set tmp_sfty_stk = isnull(A.pt_sfty_stk, 0)
    from (
          select pt_part, isnull(ptp2_sfty_stk, pt_sfty_stk) as pt_sfty_stk
          from  pt_mstr  left join ptp2_det  on pt_part = ptp2_part and ptp2_site = @site
          where pt_part between @pt_part_fr and @pt_part_to
         ) A
    where tmp_part = A.pt_part

    --库存余量
    update #tmp set tmp_qty_remain = tmp_qty_oh + tmp_qty_on_order + tmp_qty_req_open - tmp_qty_req_total - tmp_sfty_stk

    --已分配数量
    --以下分配数量必须与qty_alloc过程中一致
    --生产单已分配
    update #tmp set tmp_qty_alloc = isnull(A.wod_qty, 0)
    from (
          select wod_part, sum(wod_qty_alloc - isnull(qty, 0) * pt_um_isu_d / pt_um_isu_m) as wod_qty
          from wod_det  join #tmp on wod_part = tmp_part
                       join wo_mstr  on wod_nbr = wo_nbr and wo_lot = wod_lot
                       join pt_mstr  on wod_part = pt_part
                  left join (
                              select pkd_wo_nbr, pkd_wo_lot, pkd_seq, pkd_part,
                                  (case when pkd_qty_iss < wod_qty_alloc then pkd_qty_iss else wod_qty_alloc end) as qty
                              from (
                                    select pkd_wo_nbr, pkd_wo_lot, pkd_seq, pkd_part, wod_qty_alloc, sum(pkd_qty_iss) as pkd_qty_iss
                                    from pkd_det  join wod_det  on wod_nbr = pkd_wo_nbr and wod_lot = pkd_wo_lot and wod_seq = pkd_seq
                                                 join pk_mstr  on pk_pk = pkd_pk
                                    where exists(select * from woc_ctrl  where woc_pk_mode = '2')
                                      and (pk_site = @site)
                                      and (pkd_part between @pt_part_fr and @pt_part_to)
                                      and (pk_pst = 0)
                                      and (pkd_type = 'ISS')
                                    group by pkd_wo_nbr, pkd_wo_lot, pkd_seq, pkd_part, wod_qty_alloc
                                   ) P
                             ) W on wod_nbr = pkd_wo_nbr and wod_lot = pkd_wo_lot and wod_seq = pkd_seq
          where wo_site = @site
            and wo_status in ('F','R','A')
          group by wod_part
         ) A
    where tmp_part = A.wod_part
    --客户订单已分配
    update #tmp set tmp_qty_alloc = tmp_qty_alloc + isnull(B.sod_qty, 0)
    from (
          select sod_part, sum(sod_qty_alloc * sod_um_rate_m / sod_um_rate_d) as sod_qty
          from sod_det  join #tmp on sod_part = tmp_part
                       join so_mstr  on sod_nbr = so_nbr
                       join cm_mstr  on cm_addr = so_cust
          where so_site = @site
            and sod_status = ''
            and (cm_consignment = 0 or so_consignment = 1)
          group by sod_part
         ) B
    where tmp_part = B.sod_part
    --未审核的送货单(不包括已有分配数量的客户订单)
    update #tmp set tmp_qty_alloc = tmp_qty_alloc + isnull(B.dnd_qty_ship, 0)
    from (
          select dnd_part, sum((dnd_qty_ship + dnd_qty_spare_ship) * dnd_um_rate_m / dnd_um_rate_d) as dnd_qty_ship
          from dn_mstr  join dnd_det  on dn_dn = dnd_dn
                       join loc_mstr  on dn_site = loc_site and dnd_loc = loc_loc
                       join so_mstr  on so_nbr = dnd_so
                       join cm_mstr  on cm_addr = so_cust
          where (dn_site  = @site)
            and (dn_pst = 0)
            and (loc_nettable = 1)
            and (cm_consignment = 0 or so_consignment = 1)
            and not exists(select * from sod_det
                           where sod_nbr = dnd_so and sod_line = dnd_so_line and sod_qty_alloc > 0 and sod_status = '')
          group by dnd_part
         ) B
    where tmp_part = B.dnd_part
    --未审核的计划外出仓单
    update #tmp set tmp_qty_alloc = tmp_qty_alloc + isnull(B.movd_qty, 0)
    from (
          select movd_part, sum(movd_qty) as movd_qty
          from mov_mstr  join movd_det  on mov_mov = movd_mov
                        join loc_mstr  on movd_site = loc_site and movd_fr = loc_loc
          where (movd_site  = @site)
            and (mov_type = 'ISS')
            and (mov_pst = 0)
            and (loc_nettable = 1)
          group by movd_part
         ) B
    where tmp_part = B.movd_part
    --同地点 未审核的转仓单 且转出仓库为nettalbe 转入仓库为非nettalbe
    --跨地点 未审核的转仓单 且转出仓库为nettalbe
    update #tmp set tmp_qty_alloc = tmp_qty_alloc + isnull(B.movd_qty, 0)
    from (
          select movd_part, sum(movd_qty) as movd_qty
          from mov_mstr  join movd_det  on mov_mov = movd_mov
                        join loc_mstr lfr  on movd_site = lfr.loc_site and movd_fr = lfr.loc_loc
                        join loc_mstr lto  on movd_site2 = lto.loc_site and movd_to = lto.loc_loc
          where (movd_site  = @site)
            and (((movd_site = movd_site2) and (lto.loc_nettable = 0)) or
                 (movd_site <> movd_site2))
            and (mov_type = 'TR')
            and (mov_pst = 0)
            and (lfr.loc_nettable = 1)
          group by movd_part
         ) B
    where tmp_part = B.movd_part
    --未审核的领料单
    update #tmp set tmp_qty_alloc = tmp_qty_alloc + isnull(B.pkd_qty_iss, 0)
    from (
          select pkd_part, sum(pkd_qty_iss * pt_um_isu_d / pt_um_isu_m) as pkd_qty_iss
          from pk_mstr  join pkd_det  on pk_pk = pkd_pk
                       join loc_mstr  on pkd_loc = loc_loc and pkd_site = loc_site
                       join pt_mstr  on pt_part = pkd_part
          where (pk_site = @site)
            and (pk_pst = 0)
            and (loc_nettable = 1)
            and (pkd_type = 'ISS')
          group by pkd_part
         ) B
    where tmp_part = B.pkd_part

    --未分配
    update #tmp set tmp_qty_unalloc = tmp_qty_oh - tmp_qty_alloc

    --返回结果
    select #tmp.*, pt_desc1, pt_desc2, pt_spec, pt_um, pt_max_qty, pt_rop, pt_loc, loc_desc, pt_loc_pos, pt_ord_min, pt_ord_mult
    from #tmp join pt_mstr  on tmp_part = pt_part
         left join loc_mstr  on loc_loc = pt_loc and loc_site = @site
    order by tmp_part
