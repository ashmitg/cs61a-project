(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

;; Problem 15
;; Returns a list of two-element lists
(define (enumerate s)
  (define (helper idx lst)
    (if (null? lst)
        '()
        (cons (list idx (car lst))
              (helper (+ idx 1) (cdr lst)))))
  (helper 0 s))


;; Problem 16
;; Merges two sorted lists according to the comparator function
(define (merge cmp lst1 lst2)
  (cond
    ((null? lst1) lst2)
    ((null? lst2) lst1)
    ((cmp (car lst1) (car lst2))
     (cons (car lst1) (merge cmp (cdr lst1) lst2)))
    (else (cons (car lst2) (merge cmp lst1 (cdr lst2))))))


