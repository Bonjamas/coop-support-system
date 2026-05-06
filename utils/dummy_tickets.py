from models import Comment, Ticket, db


def dummy_ticket_data():
    if Ticket.query.first():
        return

    print("Creating dummy tickets...")

    USERS = {
        "admin":      {"oid": "a59ecfe8-c8b2-4f6c-a760-980a914c7177", "name": "Nikolaj Admin"},
        "support1":   {"oid": "c5b64939-3ba3-4352-aa68-419f453e7b3b", "name": "Benjamin Support"},
        "support2":   {"oid": "1097ed99-44ee-4a1b-8423-88fde4b5eb5f", "name": "Frederik Support"},
        "karlslunde": {"oid": "28ecb256-770c-4d8b-830f-68d936b1c96b", "name": "SuperBrugsen Karlslunde"},
        "greve":      {"oid": "7a38f75b-a896-499d-89d6-579cb367314d", "name": "365discount Greve"},
        "hvidovre":   {"oid": "3e2718de-6ead-4a85-9293-9f628722bf26", "name": "Kvickly Hvidovre"},
        "mette":      {"oid": "f1a2b3c4-1111-2222-3333-444455556666", "name": "Mette Hansen"},
        "lars":       {"oid": "a1b2c3d4-5555-6666-7777-888899990000", "name": "Lars Andersen"},
        "sofie":      {"oid": "b2c3d4e5-aaaa-bbbb-cccc-ddddeeee1111", "name": "Sofie Christensen"},
        "thomas":     {"oid": "c3d4e5f6-2222-3333-4444-555566667777", "name": "Thomas Nielsen"},
    }

    def mk(title, description, priority, state, type_, contact, creator, assignee=None):
        t = Ticket(
            title=title, description=description, priority=priority,
            state=state, type=type_, contact_info=contact,
            created_by=USERS[creator]["oid"], created_by_name=USERS[creator]["name"],
            requested_by=USERS[creator]["oid"], requested_by_name=USERS[creator]["name"],
        )
        if assignee:
            t.assigned_to = USERS[assignee]["oid"]
            t.assigned_to_name = USERS[assignee]["name"]
        return t

    def sys(text):
        return Comment(text=text, author_name="System", type="system")

    def sys_i(text):
        return Comment(text=text, author_name="System", type="system_internal")

    def note(text, author):
        return Comment(
            text=text,
            author_oid=USERS[author]["oid"],
            author_name=USERS[author]["name"],
            type="note",
        )

    def comment(text, author):
        return Comment(
            text=text,
            author_oid=USERS[author]["oid"],
            author_name=USERS[author]["name"],
            type="comment",
        )


    # =========================================================
    # I GANG — Benjamin (support1)
    # =========================================================

    t1 = mk("Kasse 3 starter ikke op",
             "Kassen tænder men går i stå under opstart. Viser fejlkode E-104. Har forsøgt genstart 3 gange.",
             "high", "in_progress", "nedbrud", "33 47 21 05", "karlslunde", "support1")
    t1.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Fejlkode E-104 peger på korrupt boot-partition. Forsøger recovery via USB.", "support1"),
        comment("Tak — vi holder kassen lukket indtil videre.", "karlslunde"),
    ]

    t2 = mk("Betalingsterminal afviser Dankort",
             "Alle Dankort afvises ved kasse 1 og 2. Visa og kontant fungerer stadig. Fejl: 'Kommunikationsfejl 51'.",
             "high", "in_progress", "nedbrud", "29 83 17 44", "greve", "support1")
    t2.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Kommunikationsfejl 51 er typisk en netværksfejl mod PBS. Tjekker forbindelsen nu.", "support1"),
        comment("Problemet opstod lige efter morgenåbning kl. 07:00.", "greve"),
        note("Bekræftet: TLS-forbindelsen til PBS gateway fejler. Eskalerer til netværksteamet.", "support1"),
    ]

    t3 = mk("Selvbetjeningskasse 2 er offline",
             "SCO-kasse 2 er gået offline og kan ikke genstartes. Skærmen er sort og reagerer ikke.",
             "high", "in_progress", "nedbrud", "33 47 21 05", "karlslunde", "support1")
    t3.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Remote-adgang virker ikke — kassen svarer ikke på netværket. Skal sandsynligvis på stedet.", "support1"),
        comment("Den gik offline midt i en transaktion. Kunden fik ikke gennemført sin betaling.", "karlslunde"),
    ]

    t4 = mk("ESL-skærme opdaterer ikke priser",
             "Elektroniske prisskilte i mejeriafdeling har ikke opdateret siden i går. Ca. 40 skilte berørt.",
             "medium", "in_progress", "funktionalitet", "44 91 28 76", "hvidovre", "support1")
    t4.comments = [
        sys("Tildelt til Benjamin Support."),
        note("ESL-gateway i Hvidovre ser ud til at have mistet forbindelsen til base-stationen. Genstarter gateway.", "support1"),
        comment("Når tror du det er oppe igen? Vi har fået nye tilbudspriser i dag.", "hvidovre"),
        note("Gateway er genstartet og begynder at synkronisere. Estimeret 30 min til fuld opdatering.", "support1"),
    ]

    t5 = mk("Ny medarbejder kan ikke logge ind på kassen",
             "Camilla Frost er oprettet i systemet men kan ikke logge ind på POS. Fejl: Invalid credentials.",
             "medium", "in_progress", "support", "33 47 21 05", "karlslunde", "support1")
    t5.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Kontoen er oprettet men ikke synkroniseret til POS-systemet endnu. Kører manuel synk.", "support1"),
        comment("Hvornår kan hun logge ind? Hun starter om 2 timer.", "karlslunde"),
    ]

    t6 = mk("Lageropgørelsessystem crasher",
             "Systemet til lageropgørelse lukker ned uden varsel ved scanning af varer i fryseafdelingen.",
             "medium", "in_progress", "nedbrud", "29 83 17 44", "greve", "support1")
    t6.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Crashet er sandsynligvis relateret til en bestemt varekategori. Beder dem teste med en specifik vare.", "support1"),
        comment("Det sker hver gang vi scanner noget fra frysevarer kategori 'Frost-B'. Andre kategorier virker.", "greve"),
        note("Reproduceret fejlen. Ser ud til at være et korrupt produktID i databasen. Undersøger.", "support1"),
    ]

    t7 = mk("Kan ikke tilgå vagtplan",
             "Får fejl 403 når jeg forsøger at åbne vagtplanen. Har prøvet i Chrome og Edge.",
             "low", "in_progress", "support", "mette.hansen@coop.dk", "mette", "support1")
    t7.comments = [
        sys("Tildelt til Benjamin Support."),
        comment("Jeg har ikke ændret noget — det virkede fint i går.", "mette"),
        note("Din bruger mangler rettighed til vagtplan-modulet. Tilføjer nu.", "support1"),
    ]

    # =========================================================
    # I GANG — Frederik (support2)
    # =========================================================

    t8 = mk("Netværk nede i hele butikken",
             "Al internet og interne systemer er nede. Kasseapparater kører i offline-mode. Opstod kl. 08:15.",
             "high", "in_progress", "nedbrud", "29 83 17 44", "greve", "support2")
    t8.comments = [
        sys("Tildelt til Frederik Support."),
        note("Router logger viser at WAN-forbindelsen droppede kl. 08:13. Kontakter ISP nu.", "support2"),
        comment("Vi har 3 kasser der ikke kan gennemføre kortbetalinger. Hvornår er det oppe?", "greve"),
        note("ISP bekræfter fejl på linje. Estimeret rettelsetid: 2 timer.", "support2"),
        comment("Okay — vi kører kontant og offline-mode indtil videre.", "greve"),
    ]

    t9 = mk("Vejemodul på selvbetjening fejler",
             "Selvbetjeningskasse 1 og 3 kan ikke veje varer. Viser: 'Vægt ikke fundet'. Kasse 2 virker.",
             "high", "in_progress", "nedbrud", "44 91 28 76", "hvidovre", "support2")
    t9.comments = [
        sys("Tildelt til Frederik Support."),
        note("Vægtenhederne på kasse 1 og 3 er ikke registreret i systemet efter sidste opdatering. Kigger på det.", "support2"),
        comment("Kunder klager — de kan ikke købe løsvægtsvarer.", "hvidovre"),
    ]

    t10 = mk("Varebestilling kan ikke sendes",
              "Elektronisk varebestilling fejler med timeout. Bestillinger gemmes ikke og vi risikerer tomme hylder.",
              "high", "in_progress", "nedbrud", "44 91 28 76", "hvidovre", "support2")
    t10.comments = [
        sys("Tildelt til Frederik Support."),
        comment("Vi har forsøgt 4 gange siden i morges. Samme fejl hver gang.", "hvidovre"),
        note("Bestillingssystemets API-endpoint svarer ikke. Ser ud til at være serversiden. Eskalerer.", "support2"),
    ]

    t11 = mk("Bonprinter udskriver ulæselige kvitteringer",
              "Kvitteringer fra kasse 4 er ulæselige — teksten er skæv og halvt afskåret. Papir og rulle er tjekket.",
              "medium", "in_progress", "support", "29 83 17 44", "greve", "support2")
    t11.comments = [
        sys("Tildelt til Frederik Support."),
        note("Printerhovedet er sandsynligvis forskudt. Beder dem tjekke om papiret er sat rigtigt i.", "support2"),
        comment("Papiret sidder korrekt. Problemet er det samme med en helt ny rulle.", "greve"),
        note("Kan se i loggen at printeren rapporterer en fejljustering. Sender vejledning til manuel kalibrering.", "support2"),
    ]

    t12 = mk("Håndscannere på lager reagerer ikke",
              "Begge trådløse håndscannere på lageret virker ikke. Batterier er skiftet og de er paret igen.",
              "medium", "in_progress", "support", "44 91 28 76", "hvidovre", "support2")
    t12.comments = [
        sys("Tildelt til Frederik Support."),
        note("Scannerene er ikke i firmwarelisten — de er muligvis ikke opdateret. Sender firmware-link.", "support2"),
        comment("Hvordan opdaterer vi dem? Vi har aldrig gjort det før.", "hvidovre"),
        note("Sender step-by-step guide på mail til kontaktadressen.", "support2"),
    ]

    t13 = mk("Adgangskode er udløbet og kan ikke nulstilles",
              "Systemet siger min adgangskode er udløbet, men nulstillingslinket virker ikke. Kan ikke logge ind.",
              "low", "in_progress", "support", "lars.andersen@coop.dk", "lars", "support2")
    t13.comments = [
        sys("Tildelt til Frederik Support."),
        comment("Jeg har tjekket spam-mappen — der er ikke noget nulstillingsmail.", "lars"),
        note("Nulstillingsmailen ryger i spam pga. manglende SPF-record på vores mailserver. Nulstiller manuelt.", "support2"),
    ]

    # =========================================================
    # I GANG — Nikolaj (admin)
    # =========================================================

    t14 = mk("Kritisk fejl i POS-integrationslag",
              "Integrationen mellem kassesystemet og regnskabsplatformen sender dubletter. Berører alle butikker.",
              "high", "in_progress", "nedbrud", "nikolaj.admin@coop.dk", "admin", "admin")
    t14.comments = [
        sys("Tildelt til Nikolaj Admin."),
        note("Fejlen opstod efter gårsdagens deploy af integrations-service v2.3.1. Ruller tilbage til v2.3.0.", "admin"),
        note("Tilbagerulning gennemført. Overvåger for nye dubletter de næste 2 timer.", "admin"),
    ]

    t15 = mk("Serverrum i Greve — unormal temperatur",
              "Temperaturalarm fra serverrum i Greve. Klimaanlæg mistænkes. Skal følges op med facility.",
              "high", "in_progress", "nedbrud", "29 83 17 44", "greve", "admin")
    t15.comments = [
        sys("Tildelt til Nikolaj Admin."),
        note("Temperatur er 28°C — grænsen er 25°C. Facility er kontaktet. Afventer svar.", "admin"),
        comment("Vi har åbnet serverrumsdøren midlertidigt for at ventilere.", "greve"),
        note("Facility bekræfter at klimaanlægget er defekt. Tekniker ankommer i morgen. Overvåger temperatur.", "admin"),
    ]

    t16 = mk("Opdatering af POS-software til v4.12",
              "Planlagt udrulning af ny POS-version til alle butikker. Koordineres med butikscheferne.",
              "medium", "in_progress", "funktionalitet", "nikolaj.admin@coop.dk", "admin", "admin")
    t16.comments = [
        sys("Tildelt til Nikolaj Admin."),
        note("Udrulning planlagt til søndag nat kl. 02:00. Butikkerne er varslet.", "admin"),
        note("Testinstallation på Karlslunde gennemført uden fejl. Fortsætter med de øvrige.", "admin"),
    ]

    # =========================================================
    # LØSTE — Nikolaj (admin)
    # =========================================================

    t17 = mk("Massiv loginproblematik efter AD-synkronisering",
              "Efter synkronisering med Active Directory kunne 12 medarbejdere på tværs af butikker ikke logge ind.",
              "high", "resolved", "nedbrud", "nikolaj.admin@coop.dk", "admin", "admin")
    t17.comments = [
        sys("Tildelt til Nikolaj Admin."),
        note("AD-synkroniseringen overskrev lokale brugerkonti med forkerte attributter. Rullet tilbage.", "admin"),
        note("Alle 12 konti er gendannet og testet. Identificerer årsagen til at synkroniseringen fejlede.", "admin"),
        sys_i("Tilstand ændret til \"Løst\" af Nikolaj Admin."),
    ]

    t18 = mk("Certifikat udløbet på betalingsgateway",
              "SSL-certifikat på betalingsgateway udløb og forårsagede fejl på alle Dankort-transaktioner.",
              "high", "resolved", "nedbrud", "nikolaj.admin@coop.dk", "admin", "admin")
    t18.comments = [
        sys("Tildelt til Nikolaj Admin."),
        note("Nyt certifikat udstedt og installeret. Betalinger virker igen. Opretter reminder 30 dage før næste udløb.", "admin"),
        sys_i("Tilstand ændret til \"Løst\" af Nikolaj Admin."),
    ]

    # =========================================================
    # NYE — Ikke tildelt (ingen kommentarer)
    # =========================================================

    t19 = mk("Kassen fryser ved kortbetaling",
             "Kasse 2 hænger fast i 2-3 minutter efter hvert kortskifte. Lange køer som følge.",
             "high", "new", "nedbrud", "33 47 21 05", "karlslunde")

    t20 = mk("Kontaktløs betaling virker ikke på nogen terminal",
             "Alle terminaler afviser MobilePay og NFC-betaling. Fejlmelding: 'Kortlæser fejl'. Chip og PIN virker.",
             "high", "new", "nedbrud", "44 91 28 76", "hvidovre")

    t21 = mk("Overvågningskamera ved indgang er sort",
             "Kameraet ved hoveddøren viser sort billede i overvågningssystemet. Andre kameraer virker.",
             "medium", "new", "nedbrud", "29 83 17 44", "greve")

    t22 = mk("10 elektroniske prisskilte er sorte i vinafdelingen",
             "10 ESL-skilte viser ingenting. Resten af skilte i butikken fungerer normalt.",
             "medium", "new", "nedbrud", "44 91 28 76", "hvidovre")

    t23 = mk("Kasseskuffe åbner ikke automatisk",
             "Kasseskuffen på kasse 1 åbner ikke ved salg og skal åbnes manuelt med nøgle hver gang.",
             "medium", "new", "support", "33 47 21 05", "karlslunde")

    t24 = mk("Kundedisplay viser forkert beløb",
             "Kundedisplayet på kasse 3 viser andre beløb end hvad kassen registrerer. Skaber forvirring.",
             "medium", "new", "funktionalitet", "29 83 17 44", "greve")

    t25 = mk("Ny medarbejder mangler adgang til lagersystem",
             "Martin Lund er oprettet men kan ikke logge ind i lagersystemet. Har brug for adgang hurtigst muligt.",
             "low", "new", "support", "44 91 28 76", "hvidovre")

    t26 = mk("Tablet til lageropgørelse starter ikke",
             "Tabletten vi bruger til lageropgørelse reagerer ikke. Har siddet i oplader natten over.",
             "medium", "new", "support", "sofie.christensen@coop.dk", "sofie")

    t27 = mk("Mangler adgang til rapporteringssystem",
             "Kan se dashboardet men ikke hente rapporter. Knappen er grå. Har brug for det til månedlig opgørelse.",
             "low", "new", "funktionalitet", "thomas.nielsen@coop.dk", "thomas")

    # =========================================================
    # LØSTE — Benjamin (support1)
    # =========================================================

    t28 = mk("POS-skærm viser forkerte priser",
              "Priser på skærmen stemte ikke overens med systemet efter prisopdatering.",
              "medium", "resolved", "funktionalitet", "44 91 28 76", "hvidovre", "support1")
    t28.comments = [
        sys("Tildelt til Benjamin Support."),
        comment("Det er specielt varer i kategori 'Mejeri' der har forkerte priser.", "hvidovre"),
        note("POS-klienten havde cachet gamle priser. Cache tømt og priser er nu korrekte.", "support1"),
        sys_i("Tilstand ændret til \"Løst\" af Benjamin Support."),
    ]

    t29 = mk("Etiketprinter virker ikke",
              "Printerens driver var korrupt efter Windows Update.",
              "medium", "resolved", "support", "33 47 21 05", "karlslunde", "support1")
    t29.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Driver er korrupt efter KB5034441-opdatering. Deinstallerer og geninstallerer driver.", "support1"),
        comment("Tak — den virker nu!", "karlslunde"),
        sys_i("Tilstand ændret til \"Løst\" af Benjamin Support."),
    ]

    t30 = mk("Medarbejder glemt PIN til kasselogin",
              "Medarbejder havde glemt sin PIN-kode.",
              "low", "resolved", "support", "29 83 17 44", "greve", "support1")
    t30.comments = [
        sys("Tildelt til Benjamin Support."),
        note("PIN nulstillet via admin-konsol. Ny midlertidig PIN sendt til butikschef.", "support1"),
        sys_i("Tilstand ændret til \"Løst\" af Benjamin Support."),
    ]

    t31 = mk("WiFi-signal svagt ved køledisk",
              "Access point ved køledisk var defekt.",
              "low", "resolved", "funktionalitet", "33 47 21 05", "karlslunde", "support1")
    t31.comments = [
        sys("Tildelt til Benjamin Support."),
        note("AP-enhed ved køledisk lyser rødt og er ude af mesh-netværket. Udskifter med reserveenhed.", "support1"),
        comment("Super — WiFi virker nu over det hele igen.", "karlslunde"),
        sys_i("Tilstand ændret til \"Løst\" af Benjamin Support."),
    ]

    t32 = mk("Dankort-terminal udskriver ikke kvittering",
              "Papirrulle var tom og siddet forkert i.",
              "low", "resolved", "support", "44 91 28 76", "hvidovre", "support1")
    t32.comments = [
        sys("Tildelt til Benjamin Support."),
        note("Guidet personalet telefonisk til at isætte ny papirrulle korrekt. Virker nu.", "support1"),
        sys_i("Tilstand ændret til \"Løst\" af Benjamin Support."),
    ]

    # =========================================================
    # LØSTE — Frederik (support2)
    # =========================================================

    t33 = mk("Kasse 1 genstarter spontant",
              "Kassen genstartet spontant hver ~30 min. Skyldtes overheatning.",
              "high", "resolved", "nedbrud", "33 47 21 05", "karlslunde", "support2")
    t33.comments = [
        sys("Tildelt til Frederik Support."),
        comment("Det er sket 4 gange i dag. Kassen er varm at røre ved.", "karlslunde"),
        note("Overheatning bekræftet — intern ventilator er støvet til. Renser og tester.", "support2"),
        comment("Den har ikke genstartet siden I var her. Tak!", "karlslunde"),
        sys_i("Tilstand ændret til \"Løst\" af Frederik Support."),
    ]

    t34 = mk("Scanner på selvbetjening skanner samme vare flere gange",
              "Scanner skannede varer 2-3 gange.",
              "high", "resolved", "nedbrud", "29 83 17 44", "greve", "support2")
    t34.comments = [
        sys("Tildelt til Frederik Support."),
        note("Kendt bug i firmware 3.1.4. Opdaterer til 3.1.6.", "support2"),
        comment("Perfekt — den fungerer normalt nu.", "greve"),
        sys_i("Tilstand ændret til \"Løst\" af Frederik Support."),
    ]

    t35 = mk("Bonprinter sætter fast ved lange kvitteringer",
              "Bonprinteren ved kasse 2 gik i stå. Printerdriverfejl efter opdatering.",
              "low", "resolved", "support", "44 91 28 76", "hvidovre", "support2")
    t35.comments = [
        sys("Tildelt til Frederik Support."),
        note("Print-driver version 4.2.1 har en kendt fejl med lange jobs. Tilbagerullet til 4.1.9.", "support2"),
        sys_i("Tilstand ændret til \"Løst\" af Frederik Support."),
    ]

    t36 = mk("Vægt ved delikatessen ude af drift",
              "Vægten viste 0 g uanset hvad der blev lagt på.",
              "high", "resolved", "nedbrud", "29 83 17 44", "greve", "support2")
    t36.comments = [
        sys("Tildelt til Frederik Support."),
        comment("Vægten har stået ude ved siden af en varmelampe — ved ikke om det har noget at sige.", "greve"),
        note("Kalibreringsfejl — sandsynligvis udløst af varme. Kalibreret og testet med kendte vægte. OK.", "support2"),
        sys_i("Tilstand ændret til \"Løst\" af Frederik Support."),
    ]

    t37 = mk("POS-terminal genstarter ved betaling",
              "Terminal ved kasse 5 genstartet ved tryk på betalingsknap.",
              "high", "resolved", "nedbrud", "44 91 28 76", "hvidovre", "support2")
    t37.comments = [
        sys("Tildelt til Frederik Support."),
        note("Strømforsyningen er defekt — viser ustabile spændinger under belastning. Udskifter.", "support2"),
        comment("Den virker perfekt nu. Mange tak for den hurtige hjælp.", "hvidovre"),
        sys_i("Tilstand ændret til \"Løst\" af Frederik Support."),
    ]

    t38 = mk("Login virker ikke efter tvunget passwordskifte",
              "Karin Mose kunne ikke logge ind efter tvunget skift.",
              "medium", "resolved", "support", "33 47 21 05", "karlslunde", "support2")
    t38.comments = [
        sys("Tildelt til Frederik Support."),
        note("Kontoen er låst efter for mange fejlede forsøg. Oplåst og ny adgangskode sat.", "support2"),
        comment("Hun kan logge ind nu. Tak!", "karlslunde"),
        sys_i("Tilstand ændret til \"Løst\" af Frederik Support."),
    ]

    db.session.add_all([
        t1, t2, t3, t4, t5, t6, t7,
        t8, t9, t10, t11, t12, t13,
        t14, t15, t16,
        t17, t18,
        t19, t20, t21, t22, t23, t24, t25, t26, t27,
        t28, t29, t30, t31, t32,
        t33, t34, t35, t36, t37, t38,
    ])

    db.session.commit()
    print("Dummy data created ✔")
