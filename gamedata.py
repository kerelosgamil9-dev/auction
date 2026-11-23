# -*- coding: utf-8 -*-
"""Game library: categories and items.
Item tuple = (tag, arabic name, english name, power). power < 0 means a prank."""

CATEGORIES = [
 dict(id="palace", ar="بناء قصر", en="Build a Palace", color=(0.55, 0.35, 0.75, 1), items=[
  ("hall", "قاعة العرش", "Throne Hall", 14), ("hall", "قاعة الاحتفالات", "Grand Ballroom", 11),
  ("hall", "المكتبة الملكية", "Royal Library", 8), ("room", "جناح الملك", "King's Suite", 10),
  ("room", "غرفة الملكة", "Queen's Chamber", 9), ("room", "مطبخ ملكي", "Royal Kitchen", 6),
  ("garden", "حدائق الورود", "Rose Gardens", 7), ("garden", "متاهة الأسوار", "Hedge Maze", 6),
  ("garden", "نافورة ذهبية", "Golden Fountain", 8), ("defense", "أبراج المراقبة", "Watch Towers", 9),
  ("defense", "الخندق المائي", "Moat", 7), ("defense", "الجسر المتحرك", "Drawbridge", 6),
  ("luxury", "تاج مرصع بالألماس", "Diamond Crown", 13), ("luxury", "سرداب الكنوز", "Treasure Vault", 12),
  ("luxury", "إسطبل الخيول الأصيلة", "Royal Stables", 7), ("luxury", "قبة من الذهب", "Golden Dome", 15),
  ("x", "تسرّب في السقف", "Leaky Roof", -5), ("x", "أشباح في القبو", "Ghosts in the Cellar", -6),
  ("x", "جيران مزعجون", "Noisy Neighbors", -3), ("x", "عمال البناء يضربون", "Builders on Strike", -7)]),
 dict(id="house", ar="بناء منزل", en="Build a House", color=(0.25, 0.6, 0.85, 1), items=[
  ("room", "غرفة نوم رئيسية", "Master Bedroom", 8), ("room", "مطبخ عصري", "Modern Kitchen", 9),
  ("room", "صالة واسعة", "Big Living Room", 8), ("room", "حمام فاخر", "Luxury Bathroom", 6),
  ("room", "غرفة ألعاب", "Game Room", 7), ("outdoor", "حديقة خضراء", "Green Garden", 7),
  ("outdoor", "مسبح", "Swimming Pool", 11), ("outdoor", "كراج لسيارتين", "Two-Car Garage", 6),
  ("outdoor", "سطح للجلسات", "Roof Terrace", 5), ("tech", "منزل ذكي", "Smart Home", 10),
  ("tech", "ألواح شمسية", "Solar Panels", 8), ("tech", "واي فاي فائق", "Fast Wi-Fi", 5),
  ("comfort", "مدفأة دافئة", "Fireplace", 6), ("comfort", "تكييف مركزي", "Central AC", 7),
  ("comfort", "سينما منزلية", "Home Cinema", 10), ("comfort", "غرفة نوم للضيوف", "Guest Room", 5),
  ("x", "سباكة مكسورة", "Broken Plumbing", -5), ("x", "نمل في المطبخ", "Ants in the Kitchen", -3),
  ("x", "جار يعزف الطبل", "Neighbor Drummer", -4), ("x", "فاتورة كهرباء ضخمة", "Huge Power Bill", -6)]),
 dict(id="restaurant", ar="بناء مطعم", en="Build a Restaurant", color=(0.9, 0.5, 0.2, 1), items=[
  ("kitchen", "شيف عالمي", "World-Class Chef", 12), ("kitchen", "فرن حجري", "Stone Oven", 8),
  ("kitchen", "مطبخ مفتوح", "Open Kitchen", 7), ("kitchen", "ثلاجة ضخمة", "Walk-in Fridge", 5),
  ("hall", "طاولات خارجية", "Patio Tables", 6), ("hall", "ركن عائلي", "Family Corner", 6),
  ("hall", "قاعة كبار الزوار", "VIP Hall", 10), ("hall", "مدخل أنيق", "Elegant Entrance", 5),
  ("menu", "قائمة سوشي", "Sushi Menu", 9), ("menu", "بيتزا إيطالية", "Italian Pizza", 8),
  ("menu", "مشويات فاخرة", "Premium Grill", 9), ("menu", "حلويات الشيف", "Chef Desserts", 7),
  ("menu", "قهوة مختصة", "Specialty Coffee", 6), ("vibe", "موسيقى حية", "Live Music", 7),
  ("vibe", "نجمة ميشلان", "Michelin Star", 14), ("vibe", "خدمة توصيل", "Delivery Service", 6),
  ("x", "ذبابة في الشوربة", "A Fly in the Soup", -6), ("x", "تقييم سيء على الإنترنت", "Terrible Review", -5),
  ("x", "نفاد الغاز", "Out of Gas", -4), ("x", "الشيف يستقيل فجأة", "Chef Quits Suddenly", -7)]),
 dict(id="beach", ar="بناء شاطئ", en="Build a Beach", color=(0.15, 0.75, 0.8, 1), items=[
  ("fun", "رياضات مائية", "Water Sports", 9), ("fun", "ملعب كرة شاطئية", "Beach Volleyball", 6),
  ("fun", "قوارب سريعة", "Speedboats", 10), ("fun", "غوص ومرجان", "Diving & Coral", 11),
  ("relax", "مظلات وكراسي", "Umbrellas & Chairs", 5), ("relax", "نادي شاطئي", "Beach Club", 9),
  ("relax", "سبا بحري", "Sea Spa", 8), ("relax", "غروب ساحر", "Magic Sunset", 7),
  ("food", "كشك مثلجات", "Ice Cream Stand", 5), ("food", "مطعم سمك", "Seafood Restaurant", 8),
  ("food", "مقهى على الرمال", "Sand Café", 6), ("safety", "برج إنقاذ", "Lifeguard Tower", 7),
  ("safety", "رمل ناعم نظيف", "Clean Soft Sand", 6), ("safety", "مياه فيروزية", "Turquoise Water", 12),
  ("safety", "مرسى يخوت", "Yacht Marina", 10), ("fun", "منزلقات مائية", "Water Slides", 8),
  ("x", "قناديل بحر", "Jellyfish Swarm", -5), ("x", "موجة عاتية", "Giant Wave", -6),
  ("x", "نورس يسرق الأكل", "Seagull Thief", -3), ("x", "طقس عاصف", "Stormy Weather", -7)]),
 dict(id="park", ar="بناء ملاهي", en="Build an Amusement Park", color=(0.9, 0.3, 0.5, 1), items=[
  ("ride", "عجلة دوّارة", "Ferris Wheel", 10), ("ride", "الأفعوانية العملاقة", "Mega Roller Coaster", 13),
  ("ride", "بيت الرعب", "Haunted House", 8), ("ride", "سيارات التصادم", "Bumper Cars", 6),
  ("ride", "برج السقوط الحر", "Drop Tower", 11), ("ride", "رحلة النهر", "Log Flume", 7),
  ("kids", "مدينة الأطفال", "Kids Zone", 6), ("kids", "الحصان الدوّار", "Carousel", 5),
  ("kids", "ملعب الرغوة", "Foam Playground", 5), ("food", "غزل البنات", "Cotton Candy", 4),
  ("food", "ساحة المطاعم", "Food Court", 6), ("show", "عرض الألعاب النارية", "Fireworks Show", 9),
  ("show", "مسرح الدمى", "Puppet Theater", 6), ("show", "قاعة ألعاب الفيديو", "Arcade", 7),
  ("show", "البوابة الذهبية", "Golden Gate", 8), ("ride", "قطار الأنفاق", "Tunnel Train", 7),
  ("x", "انقطاع الكهرباء", "Power Outage", -6), ("x", "طابور لا ينتهي", "Endless Queue", -4),
  ("x", "مهرّج مخيف", "Scary Clown", -5), ("x", "لعبة معطلة", "Broken Ride", -5)]),
 dict(id="football", ar="تكوين فريق كرة قدم", en="Football Team", color=(0.2, 0.7, 0.3, 1), items=[
  ("GK", "تيبو كورتوا", "Thibaut Courtois", 18), ("GK", "مانويل نوير", "Manuel Neuer", 17),
  ("GK", "ياسين بونو", "Yassine Bounou", 16), ("GK", "إيدرسون", "Ederson", 16),
  ("DEF", "فيرجيل فان دايك", "Virgil van Dijk", 18), ("DEF", "سيرخيو راموس", "Sergio Ramos", 17),
  ("DEF", "أشرف حكيمي", "Achraf Hakimi", 17), ("DEF", "روبن دياز", "Ruben Dias", 16),
  ("DEF", "تياغو سيلفا", "Thiago Silva", 15), ("DEF", "ترينت ألكسندر أرنولد", "Trent Alexander-Arnold", 16),
  ("MID", "كيفين دي بروين", "Kevin De Bruyne", 19), ("MID", "لوكا مودريتش", "Luka Modric", 18),
  ("MID", "رودري", "Rodri", 18), ("MID", "أندريس إنييستا", "Andres Iniesta", 18),
  ("MID", "تشافي هرنانديز", "Xavi Hernandez", 17), ("MID", "جود بيلينغهام", "Jude Bellingham", 17),
  ("ATT", "ليونيل ميسي", "Lionel Messi", 20), ("ATT", "كريستيانو رونالدو", "Cristiano Ronaldo", 20),
  ("ATT", "كيليان مبابي", "Kylian Mbappe", 19), ("ATT", "إيرلينغ هالاند", "Erling Haaland", 19),
  ("ATT", "محمد صلاح", "Mohamed Salah", 18), ("ATT", "نيمار", "Neymar", 17),
  ("ATT", "كريم بنزيمة", "Karim Benzema", 17), ("COACH", "بيب غوارديولا", "Pep Guardiola", 12),
  ("COACH", "كارلو أنشيلوتي", "Carlo Ancelotti", 12), ("COACH", "يورغن كلوب", "Jurgen Klopp", 11),
  ("x", "إصابة في الركبة", "Knee Injury", -8), ("x", "بطاقة حمراء", "Red Card", -7),
  ("x", "هدف في مرماك", "Own Goal", -6), ("x", "المدرب يستقيل", "Coach Resigns", -5)]),
 dict(id="heroes", ar="فريق أبطال خارقين", en="Superheroes Team", color=(0.2, 0.4, 0.9, 1), items=[
  ("strength", "سوبرمان", "Superman", 20), ("tech", "باتمان", "Batman", 16),
  ("strength", "المرأة الخارقة", "Wonder Woman", 18), ("speed", "فلاش", "The Flash", 17),
  ("strength", "أكوامان", "Aquaman", 15), ("magic", "الفانوس الأخضر", "Green Lantern", 15),
  ("tech", "سايبورغ", "Cyborg", 12), ("magic", "شازام", "Shazam", 16),
  ("mind", "الصياد المريخي", "Martian Manhunter", 15), ("strength", "سايتاما", "Saitama", 19),
  ("strength", "غوكو", "Goku", 20), ("speed", "سونيك", "Sonic", 13),
  ("mind", "البروفيسور إكس", "Professor X", 17), ("tech", "السيد إنكريديبل", "Mr. Incredible", 13),
  ("x", "كريبتونايت", "Kryptonite!", -9), ("x", "فقدان القوى", "Powers Lost", -7),
  ("x", "هوية مكشوفة", "Identity Exposed", -5), ("x", "قناع ممزق", "Torn Mask", -3)]),
 dict(id="marvel", ar="مارفل: أبطال وأشرار", en="Marvel Heroes & Villains", color=(0.85, 0.15, 0.2, 1), items=[
  ("hero", "الرجل الحديدي", "Iron Man", 18), ("hero", "كابتن أمريكا", "Captain America", 16),
  ("cosmic", "ثور", "Thor", 19), ("hero", "هالك", "Hulk", 19),
  ("hero", "الأرملة السوداء", "Black Widow", 12), ("hero", "سبايدرمان", "Spider-Man", 17),
  ("hero", "النمر الأسود", "Black Panther", 16), ("magic", "دكتور سترينج", "Doctor Strange", 18),
  ("magic", "الساحرة القرمزية", "Scarlet Witch", 19), ("cosmic", "كابتن مارفل", "Captain Marvel", 19),
  ("hero", "الرجل النملة", "Ant-Man", 10), ("hero", "ديدبول", "Deadpool", 14),
  ("cosmic", "ثانوس", "Thanos", 20), ("villain", "لوكي", "Loki", 15),
  ("villain", "ألترون", "Ultron", 16), ("villain", "ريد سكل", "Red Skull", 12),
  ("villain", "ماغنيتو", "Magneto", 17), ("villain", "دكتور دوم", "Doctor Doom", 18),
  ("villain", "غرين غوبلن", "Green Goblin", 12), ("villain", "فينوم", "Venom", 15),
  ("cosmic", "غالاكتوس", "Galactus", 20), ("cosmic", "هيلا", "Hela", 17),
  ("villain", "كيلمونغر", "Killmonger", 13), ("villain", "كانغ", "Kang", 16),
  ("x", "الدرع المكسور", "Broken Shield", -6), ("x", "خيانة داخل الفريق", "Betrayal in the Team", -7),
  ("x", "طقطقة ثانوس", "The Snap", -9), ("x", "ضياع حجر الإنفينيتي", "Lost Infinity Stone", -5)]),
 dict(id="zoo", ar="بناء حديقة حيوان", en="Build a Zoo", color=(0.55, 0.7, 0.2, 1), items=[
  ("cats", "الأسد", "Lion", 12), ("big", "الفيل", "Elephant", 12), ("big", "الزرافة", "Giraffe", 9),
  ("cats", "النمر", "Tiger", 11), ("big", "الدب القطبي", "Polar Bear", 10), ("special", "الشمبانزي", "Chimpanzee", 6),
  ("birds", "الببغاء الملون", "Colorful Parrot", 5), ("birds", "الطاووس", "Peacock", 6), ("birds", "النسر", "Eagle", 8),
  ("sea", "الدلفين", "Dolphin", 9), ("sea", "البطريق", "Penguin", 7), ("sea", "الأخطبوط", "Octopus", 6),
  ("special", "الباندا العملاقة", "Giant Panda", 13), ("cats", "الفهد", "Cheetah", 10),
  ("big", "التمساح", "Crocodile", 8), ("special", "الكنغر", "Kangaroo", 7),
  ("x", "هروب القرد", "Escaped Monkey", -5), ("x", "رائحة كريهة", "Awful Smell", -4),
  ("x", "مرض الحيوانات", "Sick Animals", -6), ("x", "سائح يطعم الدب", "Tourist Feeds the Bear", -4)]),
 dict(id="space", ar="بناء قاعدة فضائية", en="Build a Space Base", color=(0.3, 0.3, 0.75, 1), items=[
  ("ship", "صاروخ ثقيل", "Heavy Rocket", 12), ("ship", "مكوك فضائي", "Space Shuttle", 11),
  ("ship", "مسبار المريخ", "Mars Rover", 9), ("lab", "مختبر مداري", "Orbital Lab", 10),
  ("lab", "تلسكوب عملاق", "Giant Telescope", 8), ("power", "مفاعل صغير", "Mini Reactor", 10),
  ("power", "ألواح شمسية فضائية", "Space Solar Panels", 7), ("life", "قبة زراعية", "Farming Dome", 7),
  ("life", "مولد الأكسجين", "Oxygen Generator", 9), ("lab", "محطة اتصالات", "Comms Station", 6),
  ("life", "روبوت مساعد", "Helper Robot", 8), ("life", "بدلات فضاء", "Space Suits", 6),
  ("x", "نيزك عابر", "Passing Meteor", -7), ("x", "عطل في الأكسجين", "Oxygen Failure", -8),
  ("x", "انقطاع الاتصال", "Lost Signal", -4), ("x", "عاصفة شمسية", "Solar Storm", -6)]),
 dict(id="pirate", ar="بناء سفينة قراصنة", en="Build a Pirate Ship", color=(0.45, 0.3, 0.2, 1), items=[
  ("ship", "سفينة شراعية", "Galleon", 12), ("weapon", "مدافع ثقيلة", "Heavy Cannons", 10),
  ("loot", "خريطة الكنز", "Treasure Map", 11), ("ship", "بوصلة سحرية", "Magic Compass", 8),
  ("crew", "قبطان محنك", "Veteran Captain", 12), ("crew", "طاقم مخلص", "Loyal Crew", 8),
  ("crew", "ببغاء الكابتن", "Captain's Parrot", 4), ("weapon", "سيف ذهبي", "Golden Cutlass", 9),
  ("loot", "صندوق الجواهر", "Jewel Chest", 13), ("ship", "علم الجمجمة", "Skull Flag", 5),
  ("loot", "برميل الرُّم", "Rum Barrel", 4), ("ship", "مرساة عملاقة", "Giant Anchor", 6),
  ("x", "عاصفة هوجاء", "Raging Storm", -6), ("x", "تمرّد الطاقم", "Mutiny", -8),
  ("x", "ثقب في السفينة", "Hull Leak", -7), ("x", "هجوم الكراكن", "Kraken Attack", -9)]),
]

GENERIC = [
  ("lucky", "ورقة يانصيب رابحة", "Winning Lottery Ticket", 6), ("lucky", "حظ سعيد", "Lucky Charm", 5),
  ("lucky", "هدية مفاجئة", "Surprise Gift", 4), ("lucky", "مساعد متطوع", "Volunteer Helper", 5),
  ("lucky", "تخفيض خاص", "Special Discount", 3), ("lucky", "صديق مؤثر", "Influential Friend", 6),
  ("x", "ضريبة مفاجئة", "Surprise Tax", -4), ("x", "فأر في المخزن", "Mouse in the Storage", -3),
  ("x", "سرقة صغيرة", "Petty Theft", -5), ("x", "تأخير في التنفيذ", "Project Delay", -4),
  ("x", "قشرة موز", "Banana Peel", -2), ("x", "حريق صغير", "Small Fire", -6),
  ("x", "مقلب من الأصدقاء", "Prank from Friends", -3), ("x", "شبكة عنكبوت عملاقة", "Giant Cobweb", -2)]

ITEMS = {}            # id -> (tag, ar, en, power, category id)
CAT = {}              # id -> category dict (adds: good, prank, tags)
GEN_GOOD, GEN_PRANK = [], []
for _c in CATEGORIES:
    _c["good"], _c["prank"] = [], []
    for _i, _it in enumerate(_c["items"]):
        _id = "%s:%d" % (_c["id"], _i)
        ITEMS[_id] = _it + (_c["id"],)
        (_c["good"] if _it[3] > 0 else _c["prank"]).append(_id)
    _c["tags"] = sorted({ITEMS[i][0] for i in _c["good"]})
    CAT[_c["id"]] = _c
for _i, _it in enumerate(GENERIC):
    _id = "g:%d" % _i
    ITEMS[_id] = _it + ("g",)
    (GEN_GOOD if _it[3] > 0 else GEN_PRANK).append(_id)


def item_name(iid, lang):
    it = ITEMS[iid]
    return it[1] if lang == "ar" else it[2]
