CLASS cx_zrouter DEFINITION
  INHERITING FROM cx_static_check
  PUBLIC
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_message.
    METHODS constructor
      IMPORTING
        textid   LIKE if_t100_message=>t100key OPTIONAL
        previous LIKE previous OPTIONAL
        mv_text  TYPE string OPTIONAL.
    DATA mv_text TYPE string READ-ONLY.
ENDCLASS.