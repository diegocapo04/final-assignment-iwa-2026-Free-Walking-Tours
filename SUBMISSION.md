# Arpino Walks — Free Walking Tours

Introduction to Web Applications — exam project.
A client–server web application to manage *Free Walking Tours* in the town of **Arpino** (Frosinone, Italy).

## Target device

Designed for **desktop**, with a responsive layout (Bootstrap grid) that also adapts to tablet and mobile.

## How to run locally

```bash
pip install -r requirements.txt
python app.py            # starts the development server on http://127.0.0.1:5000
```

> The project already includes the populated SQLite database `db/database.db`
> (with all sample users, tours, photos and reservations), so no initialization
> step is required.

## What you can test

- **Anonymous user:** browse the homepage, filter tours by date / duration / language, open a tour to see its full details (schedule, stops, 5 photos).
- **Participant** (`sara`, `marco`, `giulia`): reserve a place on a tour date, add up to 3 extra people (1–4 total), cancel a reservation up to 24 h before the start, view reservations in the profile page.
- **Guide** (`luca`, `marta`): create a tour (weekly schedule, ≥4 stops, exactly 5 photos), edit a tour (essential fields are locked once a reservation exists), see reservations grouped per date, and file a **post-tour report** (declared attendees + evidence photo) for past dates.
- **Administrator** (`admin`): platform dashboard with statistics (guides, participants, tours, reservations, reservations per language) and the list of guides with their languages and tours.

### Sample data highlights

- 1 administrator, 2 guides, 3 participants.
- 4 tours with different languages (Italian, English, Spanish, German), durations and weekly schedules, each with 5 real photos of Arpino.
- Reservations including a **past date** already eligible for the post-tour report
  (log in as `luca` → *My tours* → *Reports*).

## Design choices (summary)

- **Backend:** Flask with explicit `sqlite3` access organised in per-entity DAOs; no ORM.
- **Auth:** Flask-Login with session cookies; passwords hashed with Werkzeug; role-based
  access (participant / guide / admin) and ownership checks.
- **Validation:** every form is validated both client-side (HTML5) and server-side.
- **Templates:** a single `base.html` extended by all pages (Jinja inheritance); semantic
  HTML5; external CSS (no inline styles) with a small custom theme over Bootstrap 5.

## Notes

- "Total reservations" and "reservations per language" in the admin dashboard count all
  reservation records (including cancelled ones), as historical platform figures.
- The participant overlap rule (no two reservations at the same time) is enforced
  server-side, as required by the specification.

## Photo credits

The promotional photos of the sample tours are real pictures of Arpino from
**Wikimedia Commons**, used under their respective free licenses:

| # | Subject (Commons file) | Author | License |
|---|---|---|---|
| 01 | [Mura megalitiche Arpino](https://commons.wikimedia.org/wiki/File:Mura_megalitiche_Arpino.jpg) | Bosch57 | CC0 |
| 02 | [Arpino wall](https://commons.wikimedia.org/wiki/File:Arpino_wall.JPG) | Vagabanda | Public domain |
| 03 | [Mura Torre Arpino](https://commons.wikimedia.org/wiki/File:Mura_Torre_Arpino.jpg) | Bosch57 | CC0 |
| 04 | [MuraCiclopiche1](https://commons.wikimedia.org/wiki/File:MuraCiclopiche1.jpg) | don Luigi Ippoliti | Public domain |
| 05 | [Nebbia e castello](https://commons.wikimedia.org/wiki/File:Nebbia_e_castello.jpg) | Bosch57 | CC0 |
| 06 | [Arpino panorama](https://commons.wikimedia.org/wiki/File:Arpino_panorama.jpg) | n/a | CC BY-SA 3.0 |
| 07 | [Arpino - Panorama](https://commons.wikimedia.org/wiki/File:Arpino_-_Panorama.jpg) | Piergiorgio Mariniello | CC BY-SA 3.0 |
| 08 | [Vista dall'alto di Arpino](https://commons.wikimedia.org/wiki/File:Vista_dall%27alto_di_Arpino.jpg) | Daniel Nascimento from Salvador, Brazil | CC BY-SA 2.0 |
| 09 | [Piazza - panoramio - pietro scerrato](https://commons.wikimedia.org/wiki/File:Piazza_-_panoramio_-_pietro_scerrato.jpg) | pietro scerrato | CC BY 3.0 |
| 10 | [Arpino nel Lazio](https://commons.wikimedia.org/wiki/File:Arpino_nel_Lazio.jpg) | gerry.scappaticci | CC BY 2.0 |
| 11 | [Arpino](https://commons.wikimedia.org/wiki/File:Arpino.jpg) | Gerry Scappaticci Original uploader was Luca P at  | CC BY 2.0 |
| 12 | [Arpino-w](https://commons.wikimedia.org/wiki/File:Arpino-w.jpg) | Aldo Porretta | CC BY-SA 3.0 |
| 13 | [Valle del Liri](https://commons.wikimedia.org/wiki/File:Valle_del_Liri.jpg) | Chris ALC | CC BY-SA 4.0 |
| 14 | [Una tersa giornata invernale](https://commons.wikimedia.org/wiki/File:Una_tersa_giornata_invernale.jpg) | Bosch57 | CC0 |
| 15 | [Arpino Porta Napoli](https://commons.wikimedia.org/wiki/File:Arpino_Porta_Napoli.jpeg) | Bosch57 | CC0 |
| 16 | [Arpino arcosestoacuto](https://commons.wikimedia.org/wiki/File:Arpino_arcosestoacuto.JPG) | n/a | CC BY-SA 2.0 it |
| 17 | [Panorama dell'Acropoli da est](https://commons.wikimedia.org/wiki/File:Panorama_dell%27Acropoli_da_est.jpg) | n/a | CC0 |
| 18 | [Arpino11AkrTTT P](https://commons.wikimedia.org/wiki/File:Arpino11AkrTTT_P.jpg) | Chris ALC | CC BY-SA 4.0 |
| 19 | [Sant'Andrea, Arpino, Lazio](https://commons.wikimedia.org/wiki/File:Sant%27Andrea,_Arpino,_Lazio.jpg) | gerry.scappaticci | CC BY 2.0 |
| 20 | [Facciata Chiesa Santa Maria Assunta Arpino](https://commons.wikimedia.org/wiki/File:Facciata_Chiesa_Santa_Maria_Assunta_Arpino.jpg) | Arkytech | CC0 |
