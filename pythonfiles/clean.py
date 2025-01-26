import csv

fn_in = 'points.csv'
fn_out = 'outfile.csv'

with open(fn_in, 'r') as inp, open(fn_out, 'w') as out:
    writer = csv.writer(out)
    for row in csv.reader(inp):
        if len(row)==4:
            writer.writerow(row)