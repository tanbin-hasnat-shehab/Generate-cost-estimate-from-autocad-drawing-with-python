blocktable : dialog {
  label = "Select Block Data";
  : boxed_column {
    label = "Available Properties";
    : list_box {
      key = "propList";
      height = 15;
      width = 40;
      multiple_select = true;
    }
  }
  : row {
    : button { key = "accept"; label = "OK"; is_default = true; }
    : button { key = "cancel"; label = "Cancel"; is_cancel = true; }
  }
}
