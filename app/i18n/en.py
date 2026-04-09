from app.i18n import Labels

EN_LABELS = Labels(
    # UI
    page_title="Snipe-IT Signature Forms",
    tab_asset="Asset",
    tab_user="User",
    search_placeholder_tag="Asset tag (e.g. 00173)",
    search_placeholder_user="Username (e.g. j.doe)",
    btn_lookup_asset="Look up asset",
    btn_lookup_user="Look up user",
    btn_checkout_form="Download Checkout Form",
    btn_return_form="Download Return Form",
    col_asset_tag="Asset Tag",
    col_name="Name",
    col_manufacturer="Manufacturer",
    col_model="Model",
    col_category="Category",
    col_serial="Serial No.",
    col_checkout_date="Checkout Date",
    col_return_date="Return Date",
    error_not_found="Not found. Please check the asset tag or username.",
    error_generic="An unexpected error occurred. Please try again.",
    no_assets="This user has no checked-out assets.",
    no_returned_assets="No recently checked-in assets found for this user.",
    select_all="Select all",
    # Document — shared
    doc_condition_note="The assets listed below have been inspected and are in working condition.",
    # Document — checkout
    doc_checkout_title="Asset Delivery Receipt",
    doc_issued_by="Issued By",
    doc_received_by="Received By",
    doc_date="Date",
    doc_signature="Signature",
    doc_name_surname="Name / Surname",
    # Document — return
    doc_return_title="Asset Return Receipt",
    doc_returned_by="Returned By",
    doc_received_by_admin="Received By",
)
