# UPDATES

## TEXT PART

- [ ] Reduce the json storage files to just _data.json_ (extracted one) & _sent.json_ (succesful sent).
- [ ] The _unknown_ & _failed_ status text should remain in _data.json_. (Created the _failed.csv_ but not yet implemented its connection with _data.json_)
- [ ] A feature to limit my sending rate to 48 per day.
- [ ] After sending, the delivery code should write each client and its status in the _report.csv_.

## EXTRACTION PART

- [x] Better detection for location through border colours.
- [x] After a succesful extraction, creation of _data.json_, _sent.json_ and _report.csv_ should be implemented.

## TEMPLATES PART

- [x] Remove any personal information and replace it with a placeholder.
