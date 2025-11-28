CREATE TABLE HOA_DON_THUOC (
 ma_hoa_don VARCHAR(50) NOT NULL,
 ma_thuoc VARCHAR(50) NOT NULL,
 don_vi_tinh VARCHAR(20) NOT NULL,
 so_luong INT NOT NULL,
 giam_gia DECIMAL(12,2) DEFAULT 0, 
 gia_ban DECIMAL(12,2) NOT NULL, 
 PRIMARY KEY (ma_hoa_don, ma_thuoc),
 FOREIGN KEY (ma_hoa_don) REFERENCES HOA_DON(ma_hoa_don),
 FOREIGN KEY (ma_thuoc) REFERENCES THUOC(ma_thuoc)
);