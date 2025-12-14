# ManhattanTachyon
A Discord bot designed to track Club Fan Counts, Member Activity, and Weekly Growth for Uma Musume Pretty Derby. 
using Api and sqlite for database

> **Note**: This project is currently under active development. Features may change or break without notice.

## File Structure

```
ManhattanTachyon/
├── cogs/
│   ├── Clubs_Stats.py      # Club statistics and tracking logic
│   ├── Members_Stats.py    # Member activity tracking
│   └── Staff.py            # Administrative commands
├── Database/
│   ├── AlmondData.db       # SQLite database file
│   ├── Db_Handler.py       # Database interaction logic
│   └── *.json              # Data files for import/stats
├── Service/
│   └── Api-Wrapper.py      # API communication wrapper
├── utils/
│   └── Importer.py         # Data import utilities
├── .env                    # Environment variables (Token, DB Path)
├── Main.py                 # Bot entry point
└── README.md
```

## Disclaimer

This project is an unofficial fan-made tool created for educational and community management purposes. It is not affiliated with Cygames, Inc. or the Uma Musume Pretty Derby franchise. All relevant copyrights and trademarks belong to their respective owners.
