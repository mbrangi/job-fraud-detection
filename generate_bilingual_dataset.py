"""
Generate a bilingual (English + Swahili) job advertisement dataset
for fake job detection. Produces a CSV matching the EMSCAD format.

Output: data/bilingual_job_ads.csv
"""

import csv
import random
import os

random.seed(42)

# ─────────────────────────── Swahili Templates ───────────────────────────

SW_TITLES_LEGIT = [
    "Meneja wa Mauzo", "Mhasibu Mkuu", "Afisa Mikopo", "Dereva wa Lori",
    "Karani wa Ofisi", "Mwalimu wa Shule ya Msingi", "Muuguzi Mkuu",
    "Mhandisi wa Ujenzi", "Meneja wa Rasilimali Watu", "Afisa Usalama",
    "Mhudumu wa Wateja", "Fundi Umeme", "Mpishi Mkuu", "Msanidi Programu",
    "Meneja wa Fedha", "Afisha Wahesabu", "Mratibu wa Mradi", "Mtafiti wa Soko",
    "Meneja wa Ugavi", "Mkurugenzi Mtendaji", "Katibu Tawala",
    "Mhandisi wa Mawasiliano", "Mkaguzi wa Ndani", "Afisa Uhasibu",
    "Msimamizi wa Shamba", "Mratibu wa Mafunzo", "Afisa Utumishi",
    "Mhandisi wa Mifumo", "Meneja wa Bidhaa", "Mtaalamu wa TEHAMA",
]

SW_TITLES_FAKE = [
    "FANYA KAZI NYUMBANI - MAPATO MFUKO!", "TUNAHITAJI WAFANYAKAZI HARAKA!!",
    "Fursa ya Dhahabu - KAZI NYEPESI MALIPO MAKUBWA",
    "TOA MAOMBI SASA - NASI ILIYOKUWA NA FUATILIO",
    "KAZI MPYA - $5000 KWA WIKI!", "Fursa - Tuma Pesa Kupata Kazi",
    "KAZI YA NDOTONI - Usikose NAFASI HII!",
    "MAPATO BILA KAZI - Jiunge Nasi Leo!",
    "TUNAKUPA KAZI HARAKA BILA MAHUSIANO",
    "FANYA UTAJIRI SASA - Kazi Nyumbani!",
    "Uwekezaji Wenye Faida Kubwa - Fursa Maalum",
    "Kazi ya Mtandaoni - Pata $1000 Kila Siku!",
    "Tafuta Wafanyakazi Wenzako - Tuzo Kubwa",
    "Nunua Bidhaa Zetu Kisha Upate Kazi",
    "Lipa Ili Kupata NAFASI YA KAZI",
]

SW_LOCATIONS = [
    "Dar es Salaam, Tanzania", "Arusha, Tanzania", "Mwanza, Tanzania",
    "Mbeya, Tanzania", "Dodoma, Tanzania", "Zanzibar, Tanzania",
    "Tanga, Tanzania", "Morogoro, Tanzania", "Nairobi, Kenya",
    "Mombasa, Kenya", "Kisumu, Kenya", "Nakuru, Kenya",
    "Eldoret, Kenya", "Kampala, Uganda", "Mbarara, Uganda",
]

SW_COMPANIES_LEGIT = [
    "Serengeti Breweries Limited", "CRDB Bank PLC", "NMB Bank PLC",
    "Vodacom Tanzania", "Tigo Tanzania", "Airtel Tanzania",
    "Tanzania Breweries Limited", "TANAPA", "TAZAMA",
    "KCB Bank Kenya", "Equity Bank Kenya", "Safaricom Kenya",
    "Centum Investments", "Jubilee Insurance", "UAP Old Mutual",
    "Kampala International University", "Aga Khan Hospital",
    "Precision Air", "Air Tanzania", "Azam Media Limited",
    "Bakhresa Group", "Quality Group Limited", "SIDO",
    "TCCIA", "CTI", "Tanzania Ports Authority",
    "Tanesco", "Dawasa", "Tanzania Railways Corporation",
]

SW_DEPARTMENTS = [
    "Mauzo", "Fedha", "Rasilimali Watu", "TEHAMA",
    "Ughushi", "Usalama", "Utawala", "Elimu",
    "Afya", "Ujenzi", "Usafirishaji", "Uzalishaji",
    "Utunzaji Wateja", "Masoko", "Utafiti na Maendeleo",
]

SW_REQUIREMENTS_LEGIT = [
    "Shahada ya Kwanza katika fani husika. Uzoefu wa kazi angalau miaka 2.",
    "Stashahada kutoka Chuo Kikuu kinachotambulika. Uwezo wa kufanya kazi kwa timu.",
    "Elimu ya Sekondari na uzoefu wa kazi miaka 3 katika nafasi inayofanana.",
    "Shahada ya Kwanza au Stashahada. Ujuzi wa kompyuta na mawasiliano.",
    "Cheti cha ufundi. Uzoefu wa miaka 2 katika fani husika.",
    "Shahada ya Uzamili ni faida. Uwezo wa kuongoza timu na kufanya maamuzi.",
    "Elimu ya Msingi na uzoefu wa kazi miaka 5.",
]

SW_REQUIREMENTS_FAKE = [
    "Hakuna elimu inayohitajika. Kila mtu anaweza kuomba.",
    "Lipa $50 kwa ajili ya usindikaji kisha utapata kazi mara moja!",
    "Tuma pesa kupitia M-Pesa kwa namba hii kupata nafasi ya kazi.",
    "Hakuna uzoefu unaohitajika. Wateja wetu hupata $5000 kwa wiki!",
    "Omba sasa na utapokea mafunzo ya kulipwa. Gharama ya usajili $30 tu.",
    "Tuma TZS 50,000 kwa ajili ya usindikaji wa nyaraka zako.",
    "Hakuna mahojiano. Tuma pesa tu na utaanza kazi leo!",
]

SW_DESCRIPTIONS_LEGIT = [
    "Kampuni yetu inatafuta mtaalamu mwenye ujuzi na bidii ya kufanya kazi. Nafasi hii inahusisha usimamizi wa shughuli za kila siku na kuripoti kwa Meneja Mkuu. Tunatoa mazingira mazuri ya kazi na fursa za mafunzo.",
    "Tunatafuta wataalamu wenye ujuzi wa kufanya kazi chini ya shinikizo. Nafasi hii inatoa fursa nzuri ya kukuza taaluma yako. Tafadhali tuma CV yako pamoja na barua ya motisha.",
    "Nafasi imejitokeza kwa mtu mwenye ujuzi na uzoefu. Majukumu ni pamoja na kuratibu shughuli za ofisi, kuhudumia wateja, na kuandaa ripoti. Tunatoa mshahara wa ushindani na marupurupu mengine.",
    "Kampuni yetu ina historia ndefu ya kutoa huduma bora kwa jamii. Tunatafuta mtu mwenye maadili mema ya kazi na uwezo wa kufanya kazi kwa kujitegemea.",
    "Mshahara wa ushindani na mazingira mazuri ya kazi. Tunatafuta mtu mwenye ujuzi na uzoefu katika fani husika. Fursa za mafunzo na kupanda ngazi zinapatikana.",
]

SW_DESCRIPTIONS_FAKE = [
    "NAFASI YA KIPEKEE! Pata mapato ya TZS 10,000,000 kwa mwezi bila kufanya chochote. Tuma TZS 30,000 kwa ajili ya usajili na utaanza kupata pesa mara moja. Wateja wengi wameshafanikiwa!",
    "KAZI NYEPESI - MAPATO MAKUBWA! Unahitaji tu simu na mtandao. Tuma TZS 50,000 kwa namba hii na utapata link ya kujiandikisha. Hakuna uzoefu unaohitajika. Usikose nafasi hii ya maisha!",
    "MAMBO MAKALI! Fanya kazi kwa saa chache tu na kupata milioni. Watu wengi wameshafanikiwa. Tuma pesa sasa kwa M-Pesa namba 07XX-XXX-XXX. Haraka fursa inaisha!",
    "JE, UNATAKA KUWA MILIONEA? Jiunge na timu yetu leo. Hakuna ujuzi unaohitajika. Tuma TZS 100,000 na utapata mafunzo kamili ya jinsi ya kufanya biashara hii. TAHADHARI: nafasi chache zimebaki!",
    "TUNAHITAJI WATU 10 TU - HARAKA! Pata mkopo wa biashara bila dhamana. Tuma TZS 25,000 kwa ajili ya usindikaji. Usikose nafasi hii maalum. Watu 10 tu ndio watafaidika!",
]

SW_BENEFITS_LEGIT = [
    "Mafao ya bima ya afya, mafao ya wastaafu, likizo ya kulipwa.",
    "Bima ya afya, mafuta ya safari, mlo wa ofisi.",
    "Mafunzo ya ndani na nje ya nchi, bima ya afya.",
    "Mafao kamili ya bima, posho ya usafiri, mafunzo.",
    "Bima ya afya, posho ya nyumba, likizo za kulipwa.",
]

SW_BENEFITS_FAKE = [
    "Pata pesa nyingi haraka na bila stress!",
    "Hakuna bima inayotolewa. Tunalipa kwa tume tu.",
    "Bila mkataba. Unalipwa kila siku kwa pesa taslimu.",
]

SW_INDUSTRIES = [
    "Fedha na Benki", "TEHAMA", "Elimu", "Afya",
    "Utalii", "Kilimo", "Uzalishaji", "Usafirishaji",
    "Mawasiliano", "Ujenzi", "Nishati na Maji", "Biashara",
]

SW_FUNCTIONS = [
    "Usimamizi", "Uhasibu", "TEHAMA", "Mauzo",
    "Huduma kwa Wateja", "Elimu", "Afya", "Uhandisi",
]

# ────────────────────────── English Templates ────────────────────────────

EN_TITLES_FAKE = [
    "EARN $10,000/WEEK WORKING FROM HOME!!",
    "URGENT HIRING - NO EXPERIENCE NEEDED",
    "Make Money Fast - Easy Work - Apply Now!",
    "$$$ CASH DAILY $$$ - Work From Home",
    "INTERNET MILLIONAIRE - Secret System Revealed",
    "Pay $20 Processing Fee to Start Your Dream Job",
    "CRYPTO TRADING - Turn $100 into $10000 Weekly",
    "Work Only 2 Hours Daily - Earn $5000/Month",
    "FINAL NOTICE - Limited Positions Available",
    "You've Been Selected! Claim Your Job Offer Now",
    "NO SKILLS NEEDED - Start Earning Immediately",
    "Govt Grant Job Program - Pay Application Fee",
    "Become A Millionaire Overnight - Join Now!",
    "ACT NOW! Special Recruitment - Only 5 Spots Left",
    "Earn While You Sleep - Passive Income Job",
]

EN_DESCRIPTIONS_FAKE = [
    "This is a once-in-a-lifetime opportunity! You can earn thousands without any experience. Simply pay a small processing fee of $50 to unlock your account and start earning immediately! Hundreds have already become millionaires!",
    "URGENT: We are looking for 10 motivated individuals. No degree required. Just send $25 for background check processing and you'll be assigned a high-paying position within 24 hours. This offer expires soon!",
    "Work from anywhere! Our proven system has helped thousands achieve financial freedom. For a small investment of $100 you get access to our exclusive platform. Start earning $2000+ weekly from day one!",
    "Limited positions available! Our recruiters have pre-selected you for a high-commission role. Pay just $75 to reserve your spot and receive comprehensive training materials worth $2000 absolutely free!",
    "$$$ ATTENTION $$$ Do you want to make real money online? Our program is simple: pay $40 registration fee, refer 5 friends, and earn $500 per referral. No work required - just recruit others!",
]

EN_REQUIREMENTS_FAKE = [
    "No experience needed. Must pay $50 processing fee.",
    "Must have internet access. Pay $25 for background check.",
    "No degree required. Send $100 to unlock training materials.",
    "Must be 18+. Pay registration fee of $75. No interview needed.",
    "Basic English. Must pay $40 for ID verification.",
]

# ────────────────────────── Generation Helpers ───────────────────────────

def make_legit_row(jid, lang, title_pool, desc_pool):
    title = random.choice(title_pool)
    location = random.choice(SW_LOCATIONS)
    dept = random.choice(SW_DEPARTMENTS)
    salary = f"{random.randrange(400, 3000, 50)}-{random.randrange(3500, 15000, 100)}"
    company = random.choice(SW_COMPANIES_LEGIT)
    desc = random.choice(desc_pool)
    req = random.choice(SW_REQUIREMENTS_LEGIT)
    ben = random.choice(SW_BENEFITS_LEGIT)
    telecommuting = random.choice(['0', '1'])
    has_logo = random.choice(['0', '1'])
    has_q = random.choice(['0', '1'])
    emp_type = random.choice(["Full-Time", "Part-Time", "Contract"])
    exp = random.choice(["Entry level", "Mid level", "Senior", "Manager"])
    edu = random.choice(["Bachelor's Degree", "Diploma", "Master's Degree", "High School"])
    ind = random.choice(SW_INDUSTRIES)
    func = random.choice(SW_FUNCTIONS)
    return [jid, title, location, dept, salary, company, desc, req, ben,
            telecommuting, has_logo, has_q, emp_type, exp, edu, ind, func, '0']

def make_fake_row(jid, lang, title_pool, desc_pool, req_pool, ben_pool):
    title = random.choice(title_pool)
    location = random.choice(SW_LOCATIONS)
    dept = ""
    salary = f"{random.randrange(5000, 20000, 100)}-{random.randrange(25000, 100000, 500)}"
    company = random.choice(["Mega Group Ltd", "Global Investment Corp", "Fast Cash Solutions",
                             "RichNow International", "Easy Money Ltd", "Quick Wealth Group"])
    desc = random.choice(desc_pool)
    req = random.choice(req_pool)
    ben = random.choice(ben_pool)
    telecommuting = '1'
    has_logo = random.choice(['0', '0', '0', '1'])
    has_q = random.choice(['0', '0', '1'])
    emp_type = random.choice(["Part-Time", "Contract", "Temporary", "Internship"])
    exp = random.choice(["Entry level", "No experience", "Not specified", "Intern"])
    edu = random.choice(["Not specified", "No requirement", "High School", "Any"])
    ind = random.choice(["Other", "Online Services", "Investment", "Marketing"])
    func = random.choice(["Sales", "Marketing", "Other", "Customer Service"])
    return [jid, title, location, dept, salary, company, desc, req, ben,
            telecommuting, has_logo, has_q, emp_type, exp, edu, ind, func, '1']

# ────────────────────────── Main ─────────────────────────────────────────

def main():
    rows = []

    # ── Generate Swahili legitimate ads (500) ──
    for i in range(500):
        jid = f"SWL{i+1:04d}"
        rows.append(make_legit_row(jid, 'sw', SW_TITLES_LEGIT, SW_DESCRIPTIONS_LEGIT))

    # ── Generate Swahili fake ads (500) ──
    for i in range(500):
        jid = f"SWF{i+1:04d}"
        rows.append(make_fake_row(jid, 'sw', SW_TITLES_FAKE, SW_DESCRIPTIONS_FAKE,
                                  SW_REQUIREMENTS_FAKE, SW_BENEFITS_FAKE))

    # ── Generate additional English fake ads (500 to partially balance) ──
    for i in range(500):
        jid = f"ENF{i+1:04d}"
        rows.append(make_fake_row(jid, 'en', EN_TITLES_FAKE, EN_DESCRIPTIONS_FAKE,
                                  EN_REQUIREMENTS_FAKE, SW_BENEFITS_FAKE))

    # ── Load original EMSCAD English data (17880 rows) ──
    emscad_path = os.path.join(os.path.dirname(__file__), 'fake_job_postings.csv')
    if os.path.exists(emscad_path):
        with open(emscad_path) as f:
            reader = csv.reader(f)
            header = next(reader)  # skip header
            for row in reader:
                rows.append(row)
        print(f"Loaded {len(rows) - 1500} rows from EMSCAD")
    else:
        print("EMSCAD dataset not found, generating only new data")

    random.shuffle(rows)

    # ── Output ──
    outdir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, 'bilingual_job_ads.csv')

    cols = ["job_id","title","location","department","salary_range","company_profile",
            "description","requirements","benefits","telecommuting","has_company_logo",
            "has_questions","employment_type","required_experience","required_education",
            "industry","function","fraudulent"]

    with open(outpath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(rows)

    fake_count = sum(1 for r in rows if r[-1] == '1')
    legit_count = sum(1 for r in rows if r[-1] == '0')
    print(f"\nDataset written to {outpath}")
    print(f"Total: {len(rows)}, Fake: {fake_count}, Legit: {legit_count}")
    print(f"Fake percentage: {100*fake_count/len(rows):.1f}%")

if __name__ == '__main__':
    main()
