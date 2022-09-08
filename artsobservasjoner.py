#!/usr/bin/env python3

import requests  # fades
import tqdm  # fades

API = "https://artskart.artsdatabanken.no/publicapi/"
areas = "5001"
fields = [
    "Id",
    "ScientificName",
    "TaxonId",
    "Sex",
    "Status",
    "Count",
    "Locality",
    "Habitat",
    "Latitude",
    "Longitude",
    "Projection",
    "Institution",
    "Collector",
    "CollectedDate",
]

terms = []
with open("species.txt") as species:
    for line in species.readlines():
        terms.append(line.strip())

def get_taxon_from_scientificname(term):
    taxons = requests.get(
        f"{API}/api/taxon/short",
        params={"term": term}
    ).json()
    for result in taxons:
        if result["ScientificName"] == term:
            return str(result["IntId"])

def get_observations_from_taxon(taxons):
    params={
        "Taxons": taxons,
        "Areas": areas,
        "pageSize": 1000,
    }
    results = requests.get(
        f"{API}/api/observations/list",
        params=params,
    ).json()
    yield from results["Observations"]
    total = results["TotalPages"]
    for index in tqdm.tqdm(range(1, total), desc="Pages", leave=False):
        params["pageIndex"] = index
        results = requests.get(
            f"{API}/api/observations/list",
            params=params,
        ).json()
        yield from results["Observations"]

with open("output.csv", "w") as output:
    output.write("\t".join(fields))
    output.write("\n")
    ids = [get_taxon_from_scientificname(term) for term in terms]
    taxons = ",".join(ids)
    observations = get_observations_from_taxon(taxons)
    for observation in observations:
        output.write("\t".join(str(observation[field]) for field in fields))
        output.write("\n")
