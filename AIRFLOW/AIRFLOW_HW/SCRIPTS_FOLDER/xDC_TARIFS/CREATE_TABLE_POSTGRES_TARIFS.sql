CREATE TABLE IF NOT EXISTS xdc.tarifs(
        tarif_id INTEGER,
        server_id INTEGER,
        org_tarif_id INTEGER,
        org_id INTEGER,
        sale_dict_id INTEGER,
        type INTEGER,
        descr varchar(255),
        rent INTEGER,
        archive INTEGER,
        deleted BOOLEAN
   );