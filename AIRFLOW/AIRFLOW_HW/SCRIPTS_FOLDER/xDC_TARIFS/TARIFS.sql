SELECT 
	[tarif_id]  = TARIFF_PLAN_ID, 
	[server_id] = 777,
	[org_tarif_id] = TARIFF_PLAN_ID, 
	[org_id] = 0,
	[sale_dict_id] = 0,
	[type] = 0,
	[descr] = TARIFF_PLAN_NAME2, 
	[rent] = 0,
	[archive] = 0,
	[deleted] = 0
	
FROM Rating_Discounting.dbo.TARIFF_PLAN;