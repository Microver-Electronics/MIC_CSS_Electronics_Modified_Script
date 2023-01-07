## Microver Css Electronics API Postprocessing 

- [x] Groupby timestamp
- [x] Every unique signal have own colon
- [x] If there is no signal for any signal assing it to 0
- [x] Ascii table
- [x] set granularity to 0.1
- [x] set maximum value of multiple signals
- [x] different engine different row
- [x] if there is no timestamp column, pass (try, except)
- [] every row fill with engine model, details (unique source address)
  - [x] extract all signal sources and map with engine model. 
  - [] if engine model declared get that signal source.
  - [] if not declared take something full with can id and get that signal source and link it together