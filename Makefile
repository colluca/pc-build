complete_data = $(wildcard data/complete/*.csv)
filtered_data = $(patsubst data/complete/%.csv, data/filtered/%.csv, $(complete_data))
bom = bom.xlsx

.PHONY: scrape filter bom

scrape:
	./scrape.py

filter: $(filtered_data)

bom: $(bom)

data/filtered/%.csv: %.py data/complete/%.csv
	./$<

$(bom): merge.py $(filtered_data)
	./$<
