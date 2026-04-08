from app.i18n import Labels

TR_LABELS = Labels(
    # UI
    page_title="Snipe-IT İmza Formları",
    tab_asset="Demirbaş",
    tab_user="Kullanıcı",
    search_placeholder_tag="Demirbaş etiketi (ör. 00173)",
    search_placeholder_user="Kullanıcı adı (ör. a.yilmaz)",
    btn_lookup_asset="Demirbaşı Ara",
    btn_lookup_user="Kullanıcıyı Ara",
    btn_checkout_form="Zimmet Tutanağı İndir",
    btn_return_form="İade Tutanağı İndir",
    col_asset_tag="Demirbaş No",
    col_name="Adı",
    col_manufacturer="Marka",
    col_model="Model",
    col_category="Kategori",
    col_serial="Seri No",
    col_assigned_to="Zimmetli",
    col_checkout_date="Zimmet Tarihi",
    col_return_date="İade Tarihi",
    error_not_found="Bulunamadı. Lütfen etiketi veya kullanıcı adını kontrol edin.",
    error_generic="Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.",
    no_assets="Bu kullanıcıya zimmetli demirbaş bulunmamaktadır.",
    no_returned_assets="Bu kullanıcı için son iade edilmiş demirbaş bulunamadı.",
    select_all="Tümünü seç",
    deselect_all="Seçimi kaldır",
    format_label="İndirme formatı",
    # Document — shared
    doc_condition_note="Aşağıda listelenen demirbaşlar kontrol edilmiş olup çalışır durumdadır.",
    # Document — checkout
    doc_checkout_title="Zimmet Tutanağı",
    doc_issued_by="Teslim Eden",
    doc_received_by="Teslim Alan",
    doc_date="Tarih",
    doc_signature="İmza",
    doc_name_surname="Ad / Soyad",
    # Document — return
    doc_return_title="İade Tutanağı",
    doc_returned_by="İade Eden",
    doc_received_by_admin="Teslim Alan",
)
