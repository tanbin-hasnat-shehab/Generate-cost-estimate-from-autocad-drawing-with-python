(vl-load-com)

;; -----------------------------
;; Add key-value to JSON object string
;; -----------------------------
(defun add-kv (key val str)
  (if (and key val)
    (strcat
      str
      "\"" key "\":\""
      (vl-string-subst "\\\"" "\"" (vl-princ-to-string val))
      "\","
    )
    str
  )
)

;; -----------------------------
;; Collect Attributes into flat string
;; -----------------------------
(defun GetAttFlat (/ arr att out)
  (setq out "")

  (if (= :vlax-true (vla-get-HasAttributes obj))
    (progn
      (setq arr (vlax-invoke obj 'GetAttributes))

      (foreach att arr
        (setq out
          (add-kv
            (vla-get-TagString att)
            (vla-get-TextString att)
            out
          )
        )
      )
    )
  )

  out
)

;; -----------------------------
;; Collect Dynamic Properties into flat string
;; -----------------------------
(defun GetDynFlat (/ props p out val)
  (setq out "")

  (if (= :vlax-true (vla-get-IsDynamicBlock obj))
    (progn
      (setq props (vlax-invoke obj 'GetDynamicBlockProperties))

      (foreach p props
        (setq val (vlax-variant-value (vla-get-Value p)))

        (setq out
          (add-kv
            (vla-get-PropertyName p)
            val
            out
          )
        )
      )
    )
  )

  out
)

;; -----------------------------
;; MAIN COMMAND
;; -----------------------------
(defun c:SSX (/ ss i ent obj file path first data att dyn blk)

  (setq path (strcat (getvar "DWGPREFIX") "ss.json"))

  (prompt "\nSelect objects: ")
  (setq ss (ssget))

  (if ss
    (progn

      (setq file (open path "w"))

      (write-line "[" file)

      (setq i 0
            first T
      )

      (while (< i (sslength ss))

        (setq ent (ssname ss i))
        (setq obj (vlax-ename->vla-object ent))

        (if
          (and
            (= (vla-get-ObjectName obj) "AcDbBlockReference")
            (= (vla-get-IsDynamicBlock obj) :vlax-true)
          )
          (progn

            (if (not first)
              (write-line "," file)
            )

            (setq first nil)

            (setq blk (vla-get-EffectiveName obj))
            (setq att (GetAttFlat))
            (setq dyn (GetDynFlat))

            ;; combine all key-values
            (setq data
              (strcat
                "{"
                "\"Name\":\"" blk "\","
                att
                dyn
              )
            )

            ;; remove last comma
            (if (> (strlen data) 0)
              (setq data (substr data 1 (- (strlen data) 1)))
            )

            (write-line (strcat data "}") file)
          )
        )

        (setq i (1+ i))
      )

      (write-line "]" file)
      (close file)

      (prompt (strcat "\n✔ Export complete → " path))
    )

    (prompt "\nNo objects selected.")
  )

  (princ)
(startapp "converter.exe")
)