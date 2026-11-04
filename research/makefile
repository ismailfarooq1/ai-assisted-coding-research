latexmk ?= latexmk

.PHONY: pdf clean

pdf:
	$(latexmk) -pdf -pdflatex='pdflatex -no-shell-escape %O %S' -interaction=nonstopmode -halt-on-error -outdir=build thesis.tex

clean:
	$(latexmk) -C -outdir=build thesis.tex
