from mediawiki import MediaWiki

# create a MediaWiki object
# set the url and user_agent
poe2wiki = MediaWiki(
    url="https://www.poe2wiki.net/api.php",
    user_agent="wraeclast-whisperer/0.0.1 (https://github.com/darecstowell) python-pymediawiki/0.7.4",
)

# print("== All Pages ==")
# print(poe2wiki.allpages(results=50000)) # doesn't get all pages (stops at 500)
# might need to rely on dump if we want all pages -- probably too much data

# search for a term
print("== Search ==")
print(poe2wiki.search("Ascension"))

print("== OpenSearch ==")
print(poe2wiki.opensearch("Ascension"))

print("== Suggest ==")
print(poe2wiki.suggest("Ascension Thing"))

# get the page
# ? these pages could be cached
ascension_trial_page = poe2wiki.page("Ascension Trial")

print("== Title ==")
print(ascension_trial_page.title)
# show page details
print("== Summary ==")
print(ascension_trial_page.summary)
print(ascension_trial_page.content)
# print(chaos.images)  #? ai could choose image to display
# print(chaos.references) # not sure this is needed
print("== Links ==")
print(ascension_trial_page.links)
