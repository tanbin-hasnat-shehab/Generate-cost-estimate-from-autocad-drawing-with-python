;;; Filename: BLOCKTABLE.LSP
;;; Description: Creates a table from selected dynamic block properties and attributes.
;;; Author: Gemini
;;;
;;; Usage:
;;; 1. Save this code as "BlockTable.lsp".
;;; 2. Ensure "BlockTable.dcl" is in the same folder.
;;; 3. Use the APPLOAD command in AutoCAD to load the LSP file.
;;; 4. Type "BlockTable" at the command prompt.

(defun c:BlockTable ( / *error* dcl_id blk sel ename obj dynProps att props coll pt row col tbl r)

  ;; Error handler to gracefully exit
  (defun *error* (msg)
    (if (and msg (not (eq msg "Function cancelled")))
      (princ (strcat "\nError: " msg))
    )
    (if dcl_id (unload_dialog dcl_id))
    (princ)
  )

  (vl-load-com)

  ;; Ask for table title
  (setq title (getstring T "\nEnter table name/title: "))
  (if (not title) (exit))

  ;; Select block reference
  (setq sel (entsel "\nSelect a dynamic block reference: "))
  (if sel
    (progn
      (setq ename (car sel))
      (setq obj (vlax-ename->vla-object ename))

      ;; Collect dynamic props
      (setq props '())
      (setq dynProps (vlax-invoke obj 'GetDynamicBlockProperties))
      (if dynProps
        (foreach dp dynProps
          (setq pname (vlax-get dp 'PropertyName))
          (setq pval (vlax-get dp 'Value))
          (setq props (append props (list (list pname (vl-princ-to-string pval)))))
        )
      )
      (princ (strcat "\nFound " (vl-princ-to-string (length props)) " dynamic properties."))

      ;; --- CRITICAL FIX: Collect attributes more reliably ---
      ;; The vlax-invoke function is more direct and reliable than checking 'HasAttributes'
      (setq att (vlax-invoke obj 'GetAttributes))
      (if att
        (progn
          (foreach a att
            (setq aname (vla-get-TagString a))
            (setq aval (vla-get-TextString a))
            (setq props (append props (list (list aname aval))))
          )
        )
      )
      (princ (strcat "\nFound " (vl-princ-to-string (- (length props) (length dynProps))) " attributes."))

      ;; --- DCL Dialog ---
      (setq dcl_id (load_dialog "BlockTable.dcl"))
      (if (not (new_dialog "blocktable" dcl_id))
        (progn
          (princ "\nError: Could not load BlockTable.dcl")
          (exit)
        )
      )

      ;; Fill listbox
      (start_list "propList")
      (foreach p props
        (add_list (strcat (car p) " = " (cadr p)))
      )
      (end_list)
      (princ "\nList box has been populated.")

      ;; Show dialog
      (setq selItems nil)
      (action_tile "accept" "(setq selItems (get_tile \"propList\")) (done_dialog 1)")
      (action_tile "cancel" "(done_dialog 0)")
      (setq res (start_dialog))
      (unload_dialog dcl_id)

      ;; If OK pressed
      (if (= res 1)
        (progn
          ;; Convert the space-separated string of indices into a list of integers
          (setq indices (read (strcat "(" selItems ")")))

          (setq coll '()) ; Use a list for the final data
          (setq idx 0)
          (foreach p props
            (if (member idx indices)
              (setq coll (append coll (list p)))
            )
            (setq idx (1+ idx))
          )

          ;; Check if any data was collected before trying to insert the table
          (if coll
            (progn
              ;; Insert table
              (setq pt (getpoint "\nPick insertion point for table: "))
              (if pt
                (progn
                  ;; Add the header row to the collection
                  (setq coll (cons (list "Property" "Value") coll))

                  (setq row (length coll))
                  (setq col 2)
                  (setq tbl (vla-AddTable
                               (vla-get-ModelSpace (vla-get-ActiveDocument (vlax-get-acad-object)))
                               (vlax-3d-point pt)
                               row col 3.0 8.0
                             ))

                  ;; Fill table title
                  (vla-SetText tbl 0 0 title)
                  (vla-MergeCells tbl 0 0 0 (1- col))
                  
                  ;; Fill table body with data
                  (setq r 1)
                  (foreach rowdata (cdr coll)
                    (vla-SetText tbl r 0 (car rowdata))
                    (vla-SetText tbl r 1 (cadr rowdata))
                    (setq r (1+ r))
                  )
                  (princ "\nTable created successfully.")
                )
              )
            )
            (princ "\nNo properties selected. Table not created.")
          )
        )
      )
    )
    (princ "\nInvalid selection. Please select a block.")
  )
  (princ)
)
