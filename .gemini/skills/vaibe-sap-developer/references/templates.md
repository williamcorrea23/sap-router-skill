# SAP Development Boilerplates
This reference contains standard, clean-core skeletons for common SAP artifacts.
Parent skill: vaibe-sap-developer

## Modern OO ABAP Class Template
```abap
CLASS lcl_processor DEFINITION FINAL.
  PUBLIC SECTION.
    METHODS: execute IMPORTING it_data TYPE standard table.
ENDCLASS.