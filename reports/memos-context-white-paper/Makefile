LATEXMK ?= latexmk
GS ?= gs
export SOURCE_DATE_EPOCH := 1793664000
export FORCE_SOURCE_DATE := 1

.PHONY: all render clean
all: paper.pdf

paper.pdf: paper.tex references.bib
	mkdir -p build
	$(LATEXMK) -g -pdf -pdflatex='pdflatex -no-shell-escape %O %S' -interaction=nonstopmode -halt-on-error -outdir=build paper.tex
	cp build/paper.pdf paper.pdf

render: paper.pdf
	mkdir -p build/preview
	$(GS) -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r150 -sOutputFile=build/preview/page-%02d.png paper.pdf

clean:
	$(LATEXMK) -C -outdir=build paper.tex
