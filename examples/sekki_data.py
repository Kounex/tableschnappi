"""
sekki_data.py — 二十四節気 (Nijūshi Sekki) Solar Term Data

All 24 Japanese solar terms with seasonal ingredient guidance for
ingestion into the Sakura Japanese Restaurant RAG system.

Order: Shōkan (1, Jan 5) through Tōji (24, Dec 22).

Provenance: the 24 solar terms, their kanji and their dates are traditional
and in the public domain. The English descriptions, nature signs, ingredient
notes and haiku in this file were written for this project (LLM-assisted) and
are covered by the repository's MIT licence — they are not reproductions of
any published almanac or translation.

This is fictional demo content for a fictional restaurant. The health_wisdom
entries are flavour text, not culinary or medical advice.
"""

SEKKI = [
    {
        "id": "shokan",
        "kanji": "小寒",
        "romaji": "Shōkan",
        "english": "Minor Cold",
        "start_month": 1,
        "start_day": 5,
        "number": 1,
        "description": (
            "The cold settles into the landscape with quiet authority as the sun traces its lowest arc. "
            "Still ponds glaze to ice by morning and bare trees cast blue shadows on pale earth. "
            "This is not yet the deepest cold, but the body begins to understand what winter truly means."
        ),
        "nature_signs": [
            "Ponds and slow rivers develop a rim of ice at their edges",
            "Wild boar tracks press deep into frost-hardened ground",
            "Japanese white-eyes pick at the last dried berries on bare branches",
            "Narcissus blooms near south-facing stone walls, the only flower brave enough",
        ],
        "shun_ingredients": [
            {"name_ja": "鰤", "name_en": "Buri (Japanese yellowtail)", "note": "Migrating south through cold winter currents, fat content peaks now; sashimi is marbled like fine wagyu."},
            {"name_ja": "鱈", "name_en": "Tara (Pacific cod)", "note": "Spawning season firms the flesh and produces prized white shirako (milt); roe is also at peak."},
            {"name_ja": "牡蠣", "name_en": "Kaki (Pacific oyster)", "note": "Cold water produces the creamiest, richest oysters of the year; the 'R-month' rule holds emphatically here."},
            {"name_ja": "白菜", "name_en": "Hakusai (napa cabbage)", "note": "Frost converts starches to sugar; slow-simmered winter hakusai is silky and deeply nourishing."},
            {"name_ja": "大根", "name_en": "Daikon (white radish)", "note": "Cold soil concentrates sweetness; winter daikon simmered in dashi becomes almost translucent and gentle."},
            {"name_ja": "柚子", "name_en": "Yuzu", "note": "Harvested through January; the essential oils in the skin are most fragrant under winter cold."},
        ],
        "health_wisdom": (
            "Focus on warming, slow-cooked foods that build internal heat: root vegetables, rich broths, and fatty winter fish. "
            "Avoid raw, cold preparations that tax the digestive system in this coldest season. "
            "Miso soup with winter vegetables twice daily is traditional winter shokuiku practice."
        ),
        "sakura_recommendations": [
            "Slow-simmered buri daikon — yellowtail and winter radish braised in sweet soy with yuzu peel and mitsuba",
            "Tara shirako ponzu — fresh cod milt served warm with citrus ponzu and momiji oroshi",
        ],
        "haiku": "Bare branches hold cold / the first crow calls through still air / winter deepens now",
    },
    {
        "id": "daikan",
        "kanji": "大寒",
        "romaji": "Daikan",
        "english": "Major Cold",
        "start_month": 1,
        "start_day": 20,
        "number": 2,
        "description": (
            "The coldest fortnight of the year arrives: river ice thickens, breath plumes in the predawn dark, "
            "and even the sea seems to slow. "
            "This was traditionally the time to begin fermenting miso and pressing sake, processes that require "
            "the clean cold to work their slow alchemy."
        ),
        "nature_signs": [
            "River ice reaches its maximum thickness of the year",
            "Miso fermenting in cedar barrels beneath farmhouse floors",
            "Sparrows fluff themselves into round balls against the cold",
            "Plum buds swell tight on bare branches, days away from opening",
        ],
        "shun_ingredients": [
            {"name_ja": "鰤", "name_en": "Buri (Japanese yellowtail)", "note": "Absolute peak: 'kan-buri' (cold-water yellowtail) is the season's most celebrated fatty fish."},
            {"name_ja": "牡蠣", "name_en": "Kaki (Pacific oyster)", "note": "January oysters raised in the coldest water of the year are supremely creamy and briny-sweet."},
            {"name_ja": "春菊", "name_en": "Shungiku (chrysanthemum greens)", "note": "Cold firms the leaves and concentrates a herbal bitterness that cleans the palate after rich winter fish."},
            {"name_ja": "牛蒡", "name_en": "Gobō (burdock root)", "note": "Winter burdock is fully mature; the earthy mineral depth is ideal for kinpira and long braises."},
            {"name_ja": "金柑", "name_en": "Kinkan (kumquat)", "note": "Tiny citrus that ripens fully in January; the sweet skin and tart flesh are eaten whole as a digestif."},
            {"name_ja": "昆布", "name_en": "Kombu (kelp)", "note": "Aged Rishiri and Rausu kombu delivers the deepest, most complex winter dashi; foundation of the season's broths."},
        ],
        "health_wisdom": (
            "This is the year's most important moment to support the kidneys and adrenals with salty, warm foods: "
            "miso, kombu dashi, and black sesame are traditional Daikan tonic ingredients. "
            "Avoid cold drinks entirely and favor ginger, cinnamon, and negi in daily cooking."
        ),
        "sakura_recommendations": [
            "Kan-buri sashimi — thick-cut yellowtail served with tosa shoyu, freshly grated ginger, and thinly sliced negi",
            "Oyster and hakusai nabe — winter hot pot finished with ponzu and momiji oroshi at the table",
        ],
        "haiku": "Ice seals the river / breath mists in the frozen dawn / the world holds its breath",
    },
    {
        "id": "risshun",
        "kanji": "立春",
        "romaji": "Risshun",
        "english": "Start of Spring",
        "start_month": 2,
        "start_day": 4,
        "number": 3,
        "description": (
            "Spring arrives on the calendar before it arrives in the sky, and this gap between the named and the felt "
            "is itself a kind of seasonal wisdom. "
            "The day before Risshun is Setsubun, when roasted soybeans are scattered to drive out winter's demons. "
            "Temperatures remain low but the plum tree, trusting the almanac more than the thermometer, pushes its first buds."
        ),
        "nature_signs": [
            "Plum blossoms open on bare branches, the first flower of the year",
            "The first uguisu (Japanese bush warbler) songs are heard in mild southern valleys",
            "Nanohana (canola) fields flush yellow in warm coastal lowlands",
            "Days visibly lengthen; the late-afternoon light takes on a new, slightly warmer angle",
        ],
        "shun_ingredients": [
            {"name_ja": "菜の花", "name_en": "Nanohana (canola blossoms)", "note": "First brassica of spring; slight bitterness is the traditional signal of the seasonal turn."},
            {"name_ja": "蛤", "name_en": "Hamaguri (hard clam)", "note": "Associated with Hinamatsuri (Mar 3); peaks in February-March as waters begin warming."},
            {"name_ja": "鰯", "name_en": "Iwashi (Japanese sardine)", "note": "Eaten at Setsubun by tradition; early-spring sardines are plump from winter feeding."},
            {"name_ja": "蕗の薹", "name_en": "Fuki no tō (butterbur sprout)", "note": "First mountain vegetable of the year; bitter-herbal flavor symbolizes the season's awakening."},
            {"name_ja": "苺", "name_en": "Ichigo (strawberry)", "note": "Japanese greenhouse strawberries — Amaou, Tochiotome — reach peak sweetness in February."},
            {"name_ja": "若布", "name_en": "Wakame (seaweed)", "note": "Spring-harvested fresh wakame is tender and brilliantly green, far more delicate than the dried year-round product."},
        ],
        "health_wisdom": (
            "Spring's bitter vegetables — nanohana, fuki no tō — are traditional liver-cleansing foods after winter's rich diet; "
            "embrace the bitterness rather than blanching it away. "
            "Light clam soups replace heavy root-vegetable stews as the body begins its own seasonal transition."
        ),
        "sakura_recommendations": [
            "Nanohana ohitashi — blanched canola blossoms dressed in dashi, mirin, and shoyu with katsuobushi",
            "Hamaguri clear soup — clams opened in sake and dashi, finished with yuzu zest and mitsuba",
        ],
        "haiku": "On the calendar / spring arrives before the warmth / hope is its own warmth",
    },
    {
        "id": "usui",
        "kanji": "雨水",
        "romaji": "Usui",
        "english": "Rain Water",
        "start_month": 2,
        "start_day": 19,
        "number": 4,
        "description": (
            "Snow yields to rain and ice to flowing water as the earth begins accepting moisture for the season ahead. "
            "The quality of precipitation changes — softer, warmer, more patient — and dormant seeds sense the permission "
            "to begin germination. "
            "Kitchen preparations shift toward lighter, wetter dishes that honor the season's invitation to move and flow."
        ),
        "nature_signs": [
            "Snow retreats to higher elevations as valley rain replaces it",
            "Ice thaws near river banks; the sound of flowing water returns",
            "Plum blossoms are at full peak, filling parks with fragrance after the rain",
            "First fuki no tō (butterbur) shoots push through softening soil on hillsides",
        ],
        "shun_ingredients": [
            {"name_ja": "蛤", "name_en": "Hamaguri (hard clam)", "note": "Peak season; the meaty, sweet flesh is at its most concentrated before spawning begins."},
            {"name_ja": "浅蜊", "name_en": "Asari (Manila clam)", "note": "Emerging from winter torpor; glycogen-rich and sweet as intertidal water temperatures rise."},
            {"name_ja": "菜の花", "name_en": "Nanohana (canola blossoms)", "note": "In full-bloom peak; the yellow flowers are edible and the stems at maximum tenderness."},
            {"name_ja": "独活", "name_en": "Udo (Japanese spikenard)", "note": "Wild udo emerges from softening hillside soil; the ivory stems have a unique herbal-celery quality unique to this season."},
            {"name_ja": "苺", "name_en": "Ichigo (strawberry)", "note": "Continued peak; late-February Japanese strawberries achieve maximum sugar-acid balance."},
            {"name_ja": "鰊", "name_en": "Nishin (Pacific herring)", "note": "Spawning runs begin on Hokkaido coasts; the roe (kazunoko) is prized for its delicate, papery crunch."},
        ],
        "health_wisdom": (
            "The body begins its spring detoxification; bitter and sour flavors — nanohana, udo, rice vinegar — "
            "support this process while providing the nutrients needed for increased activity. "
            "Clam soups replenish minerals depleted over winter."
        ),
        "sakura_recommendations": [
            "Udo shiraae — udo batons dressed in silken tofu crushed with white sesame, mirin, and miso",
            "Fuki no tō tempura — bitter butterbur sprouts fried light and served with mountain salt and sudachi",
        ],
        "haiku": "Cold rain on bare clay / the plum refuses to wait / pink against gray sky",
    },
    {
        "id": "keichitsu",
        "kanji": "啓蟄",
        "romaji": "Keichitsu",
        "english": "Insects Awaken",
        "start_month": 3,
        "start_day": 6,
        "number": 5,
        "description": (
            "Thunder cracks the dormant sky and vibrates the soil, calling earthworms and beetles upward from their winter retreats. "
            "Mountain sides show the first tentative green as wild herbs and ferns unfurl their tightly coiled shapes toward light. "
            "The Japanese kitchen looks eagerly to the hillsides as foragers begin bringing down sansai — the wild mountain vegetables "
            "that taste of pure awakening."
        ),
        "nature_signs": [
            "Earthworms emerge after the first warm rains and first thunder",
            "Warabi (bracken fern) fiddleheads uncurl on south-facing slopes",
            "Tara no me (angelica sprouts) push through dead leaves in mountain clearings",
            "Sea bream schools move into shallower spawning grounds near the coast",
        ],
        "shun_ingredients": [
            {"name_ja": "竹の子", "name_en": "Takenoko (bamboo shoots)", "note": "First shoots of the season emerge in warmer western Japan; ivory flesh is sweet and must be cooked the day it is cut."},
            {"name_ja": "タラの芽", "name_en": "Tara no me (angelica sprouts)", "note": "Wild mountain vegetable foraged just as it unfurls; the slight bitterness and delicate structure are irreplaceable."},
            {"name_ja": "蕨", "name_en": "Warabi (bracken fern)", "note": "Fiddleheads processed with ash water to remove harshness; the result is silky and faintly bitter."},
            {"name_ja": "鯛", "name_en": "Tai (sea bream)", "note": "Spring is tai's definitive season; moving into spawning grounds, the flesh becomes richer and the skin flushes pink."},
            {"name_ja": "浅蜊", "name_en": "Asari (Manila clam)", "note": "Still at peak; warm soups and sake-steamed preparations highlight the natural sweetness."},
            {"name_ja": "桜海老", "name_en": "Sakura ebi (cherry shrimp)", "note": "Spring catch season opens in Suruga Bay; tiny translucent shrimp with intense sweet-savory flavor used in kakiage."},
        ],
        "health_wisdom": (
            "Wild mountain vegetables are nature's spring tonic: their bitterness stimulates bile production and supports "
            "the liver's seasonal cleansing cycle. "
            "Eat lightly dressed sansai at the start of meals to prepare digestion for the richer fish that follow."
        ),
        "sakura_recommendations": [
            "Takenoko gohan — bamboo shoot rice cooked in dashi with kinome leaf garnish and sea salt",
            "Tara no me and sakura ebi kakiage — mixed tempura fritter with mountain herb salt",
        ],
        "haiku": "Beneath cold loam earth / something small remembers light / a tendril uncurls",
    },
    {
        "id": "shunbun",
        "kanji": "春分",
        "romaji": "Shunbun",
        "english": "Spring Equinox",
        "start_month": 3,
        "start_day": 21,
        "number": 6,
        "description": (
            "Day and night are held in perfect balance before tipping toward warmth and light. "
            "This is Ohigan — a time to visit ancestors' graves, tend the continuity between living and gone, "
            "and eat the ohagi sweet rice balls offered at household altars. "
            "Sea bream — called sakura-dai for the pink flush of its spawning season — leaps through currents "
            "with energy that mirrors the cherry blossoms opening above."
        ),
        "nature_signs": [
            "Cherry blossoms open in southern Japan; the hanami season begins",
            "Sea bream school in spawning grounds close to shore, their sides flushed pink",
            "Tsukushi (horsetail shoots) appear in sunny meadow patches",
            "Swallows are sighted for the first time, arriving from Southeast Asia",
        ],
        "shun_ingredients": [
            {"name_ja": "鯛", "name_en": "Sakura-dai (spring sea bream)", "note": "The name 'cherry blossom sea bream' is given at equinox; the flesh is richer, the skin its most vivid pink."},
            {"name_ja": "竹の子", "name_en": "Takenoko (bamboo shoots)", "note": "Full spring peak; shoots must be boiled the day they are dug to preserve sweetness."},
            {"name_ja": "蛤", "name_en": "Hamaguri (hard clam)", "note": "Traditional for Hinamatsuri and spring Ohigan; paired halves symbolize a perfect marital union."},
            {"name_ja": "独活", "name_en": "Udo (Japanese spikenard)", "note": "At its most tender and fragrant before the stems become fibrous; excellent raw in sunomono."},
            {"name_ja": "木の芽", "name_en": "Kinome (sansho sprouts)", "note": "Tiny fragrant leaves of the Japanese pepper tree; their citrus-peppery aroma is peak only in spring."},
            {"name_ja": "苺", "name_en": "Ichigo (strawberry)", "note": "Late-March peak of outdoor-grown varieties; sweetness deepens with longer days."},
        ],
        "health_wisdom": (
            "The equinox is a hinge point: allow the diet to pivot from the dense richness of winter toward "
            "lighter, more vegetable-forward meals that support the body's seasonal expansion. "
            "The traditional ohagi (sweet rice with anko) is not mere ceremony — the red bean provides iron and fiber "
            "as the body increases its activity."
        ),
        "sakura_recommendations": [
            "Sakura-dai salt-grilled whole — spring sea bream with kinome miso and bamboo shoot on the side",
            "Hamaguri clear soup — clams in sake and kombu dashi with mitsuba and yuzu, served for Ohigan",
        ],
        "haiku": "Day holds night in check / the sea bream leaps at first light / equal now at last",
    },
    {
        "id": "seimei",
        "kanji": "清明",
        "romaji": "Seimei",
        "english": "Clear and Bright",
        "start_month": 4,
        "start_day": 5,
        "number": 7,
        "description": (
            "The haze of winter has lifted completely and the air rinses the world clean; every color appears "
            "in its purest, most saturated register. "
            "Swallows stitch arcs across a sky that is now decisively blue, and cherry petals drift in spirals "
            "that look almost ceremonial. "
            "Japanese tradition has long understood that visual beauty nourishes the body as directly as food does, "
            "and this fortnight is the year's most potent dose."
        ),
        "nature_signs": [
            "Cherry blossom season peaks and petals fall in drifts along canal banks",
            "Swallows perform their first aerial displays over paddies and rivers",
            "Spring cabbage hearts open, pale and tender, in farm fields",
            "Bamboo shoots push through the forest floor in such numbers they can be heard at dawn",
        ],
        "shun_ingredients": [
            {"name_ja": "竹の子", "name_en": "Takenoko (bamboo shoots)", "note": "Absolute prime; the ivory flesh is sweet and the bitter notes minimal when cooked immediately after harvest."},
            {"name_ja": "鰆", "name_en": "Sawara (Japanese Spanish mackerel)", "note": "The kanji for sawara contains 'spring'; firm white flesh with a clean ocean sweetness, ideal for saikyo-yaki."},
            {"name_ja": "春キャベツ", "name_en": "Haru kyabetsu (spring cabbage)", "note": "Loose, tender leaves with high water content and natural sweetness; needs almost no cooking."},
            {"name_ja": "新玉葱", "name_en": "Shin tamanegi (new onion)", "note": "Spring onions with thin skin and mild sweetness; can be eaten raw, grilled whole, or floated in clear soup."},
            {"name_ja": "桜海老", "name_en": "Sakura ebi (cherry shrimp)", "note": "Spring peak in Suruga Bay; deep-fried or sun-dried, the concentrated umami is extraordinary."},
            {"name_ja": "苺", "name_en": "Ichigo (strawberry)", "note": "Closing weeks of peak season; outdoor-grown April strawberries have maximum complexity."},
        ],
        "health_wisdom": (
            "The 'clear and bright' quality of this season calls for correspondingly clear flavors: "
            "light dashi, delicate steaming, and minimal seasoning to let spring ingredients speak. "
            "Support eye health and liver function with dark leafy greens and the chlorophyll-rich flavors abundant now."
        ),
        "sakura_recommendations": [
            "Sawara saikyo-yaki — Spanish mackerel marinated in sweet Kyoto white miso, broiled and served with bamboo shoot",
            "Takenoko to kinome ae — bamboo shoots dressed with fragrant sansho-bud miso and sesame",
        ],
        "haiku": "Clear and rinsed the air / cherry petals drift like snow / light makes shadows thin",
    },
    {
        "id": "kokuu",
        "kanji": "穀雨",
        "romaji": "Kokuu",
        "english": "Grain Rain",
        "start_month": 4,
        "start_day": 20,
        "number": 8,
        "description": (
            "Steady rains fall to nourish the newly planted grain, soaking into paddies that farmers have carefully prepared. "
            "In tea country, the first flush of shincha is harvested with great ceremony — tenderest of all teas, "
            "with the highest L-theanine and the freshest flavor of the year. "
            "Katsuo (bonito) make their first northward migration through warm Kuroshio current waters, celebrated as "
            "'hatsu-gatsuo' with the reverence given to any season's first gift."
        ),
        "nature_signs": [
            "Rice seedlings transplanted into prepared paddies in southern Japan",
            "Tea pickers in Uji and Shizuoka harvest the first flush of shincha",
            "Wisteria blooms heavy with rain at shrine gates",
            "Katsuo (bonito) schools detected off Tosa coast, moving northeast",
        ],
        "shun_ingredients": [
            {"name_ja": "初鰹", "name_en": "Hatsu-gatsuo (first bonito)", "note": "The year's inaugural katsuo run: lean, firm, and exhilarating; Edo tradition says to eat it even if you must pawn your coat."},
            {"name_ja": "新茶", "name_en": "Shincha (first-flush tea)", "note": "Ceremonial new tea harvested before rainy season; lowest bitterness, highest nutrients, intensely vegetal and fresh."},
            {"name_ja": "空豆", "name_en": "Soramame (fava beans)", "note": "Sky beans face upward to the rain; tender young pods barely need cooking and taste of spring air."},
            {"name_ja": "アスパラガス", "name_en": "Asuparagasu (asparagus)", "note": "Hokkaido asparagus season opens; tight-tipped green spears with a sweetness that the northern climate uniquely develops."},
            {"name_ja": "新玉葱", "name_en": "Shin tamanegi (new onion)", "note": "Peak sweetness; the season's mild onions eaten raw in paper-thin slices with katsuobushi and ponzu."},
            {"name_ja": "竹の子", "name_en": "Takenoko (bamboo shoots)", "note": "Final weeks; late-April bamboo shoots have more character and slightly more bitterness — ideal for kinpira."},
        ],
        "health_wisdom": (
            "Shincha drunk in the morning provides antioxidants and L-theanine to support mental clarity "
            "during the busy agricultural season. "
            "New spring onions eaten raw tonify the lungs and protect against late-spring colds."
        ),
        "sakura_recommendations": [
            "Hatsu-gatsuo tataki — first bonito seared over straw, served with ginger, garlic chips, and Tosa shoyu",
            "Soramame and new onion kakiage — fava bean and spring onion tempura fritter with shincha salt",
        ],
        "haiku": "First tea steams the cup / green fields await the thunder / rains come like a gift",
    },
    {
        "id": "rikka",
        "kanji": "立夏",
        "romaji": "Rikka",
        "english": "Start of Summer",
        "start_month": 5,
        "start_day": 6,
        "number": 9,
        "description": (
            "Summer announces itself not with fanfare but with a specific warmth the body recognizes — "
            "the first sweat of the year forming before exertion begins. "
            "Swallows wheel over paddies where transplanted seedlings stand in neat rows; katsuo surge northward "
            "through waters turned green-blue with summer plankton. "
            "The kitchen pivots from the introspective richness of spring mountain vegetables to the extroverted "
            "brightness of early summer."
        ),
        "nature_signs": [
            "Swallows build mud nests under eaves and on bridge beams",
            "Katsuo schools move north of Shikoku; fishermen deploy pole-and-line boats",
            "Hillsides complete their transformation to a uniform, vivid green",
            "Spring flowers give way to iris and wisteria along temple paths",
        ],
        "shun_ingredients": [
            {"name_ja": "鰹", "name_en": "Katsuo (bonito)", "note": "Full northward migration; the spring run is lean and clean, best tataki-style to showcase the direct ocean flavor."},
            {"name_ja": "鱚", "name_en": "Kisu (sillago/whiting)", "note": "Delicate early-summer white fish that makes perfect tempura; the flesh is sweet and barely needs seasoning."},
            {"name_ja": "空豆", "name_en": "Soramame (fava beans)", "note": "Final peak week before the pods harden; the freshest beans eaten immediately after shelling."},
            {"name_ja": "アスパラガス", "name_en": "Asuparagasu (asparagus)", "note": "Hokkaido peak; varieties grown for flavor over yield with exceptional sweetness in the thick spears."},
            {"name_ja": "新生姜", "name_en": "Shin shōga (new ginger)", "note": "Young ginger is mild, fresh, and pink-tipped; softer and less fibrous than mature rhizomes, excellent pickled or sliced raw."},
            {"name_ja": "いさき", "name_en": "Isaki (grunt fish)", "note": "A summer coastal fish that begins its season now; delicate white flesh with clean sweetness, best as sashimi."},
        ],
        "health_wisdom": (
            "Begin eating cooling foods — cucumber, summer herbs, light noodle dishes — as the body prepares for summer's demands. "
            "New ginger aids circulation and prevents the stagnation that early summer humidity can cause."
        ),
        "sakura_recommendations": [
            "Katsuo tataki with myōga, shiso chiffonade, and kabosu ponzu — summer's opening statement",
            "Kisu tempura — whiting in light batter with sea salt and squeezed sudachi",
        ],
        "haiku": "Swallows cut blue sky / katsuo breaks the surface / summer announced now",
    },
    {
        "id": "shoman",
        "kanji": "小満",
        "romaji": "Shōman",
        "english": "Grain Buds",
        "start_month": 5,
        "start_day": 21,
        "number": 10,
        "description": (
            "Grain ears form in the paddies — small and perfect, proof that summer's work proceeds. "
            "The air grows thick with humidity and the landscape fills with sound: frogs, the first cicadas tuning up, "
            "irrigation water rushing through bamboo channels. "
            "The first green plums appear in markets, and the urgency of ume-picking season begins — these fruits "
            "will fall when fully ripe."
        ),
        "nature_signs": [
            "Rice ears visible and filling in paddies across Kyushu and western Japan",
            "Green plums hang heavy on ume trees, just days from harvest urgency",
            "The first fireflies of the year are seen on warm evenings near slow streams",
            "Cicadas begin their tentative first calls in the warmest valleys",
        ],
        "shun_ingredients": [
            {"name_ja": "鰹", "name_en": "Katsuo (bonito)", "note": "Continuing northward; fat content building slightly, making the flesh richer than the leaner April fish."},
            {"name_ja": "鰺", "name_en": "Aji (horse mackerel)", "note": "Aji enters its long summer peak; the quintessential summer fish for tataki, nanban-zuke, and fresh sashimi."},
            {"name_ja": "青梅", "name_en": "Aoume (green plum)", "note": "Tart, firm, and aromatic before ripening; used now for umeshu, cordials, and pickled condiments."},
            {"name_ja": "新じゃが", "name_en": "Shin jaga (new potato)", "note": "Fresh-dug small potatoes from Nagasaki and Kagoshima; skin-on simmering in dashi brings out a creaminess impossible in stored tubers."},
            {"name_ja": "胡瓜", "name_en": "Kyūri (cucumber)", "note": "First cucumbers of summer; thin-skinned and tender with an intensely fresh, clean green flavor."},
            {"name_ja": "飛魚", "name_en": "Tobiuo (flying fish)", "note": "Spring-summer specialty prized in Kyushu and Yakushima; the dramatic leaping fish is best as sashimi or lightly cured."},
        ],
        "health_wisdom": (
            "Green plum vinegar and umeboshi are traditional early-summer foods that stimulate appetite suppressed by heat "
            "and restore the citric acid cycle depleted by humidity. "
            "Sour flavors now begin their six-month reign as digestive and cooling medicine."
        ),
        "sakura_recommendations": [
            "Aji tataki with grated ginger, myōga, and ponzu — summer horse mackerel at its freshest",
            "Aoume no hachimitsu-zuke — green plum pickled in honey, served as a digestif amuse-bouche",
        ],
        "haiku": "Green ears fill with light / the paddy hums with new life / nothing is enough",
    },
    {
        "id": "boshu",
        "kanji": "芒種",
        "romaji": "Bōshu",
        "english": "Grain in Ear",
        "start_month": 6,
        "start_day": 6,
        "number": 11,
        "description": (
            "The awns of rice and barley are now visible and forming — the most intensive period of the rice cycle, "
            "when the paddies need constant attention. "
            "Fireflies appear at dusk along slow streams, blinking cold light into heavy humid air. "
            "Plum harvest reaches peak urgency as falling ume must be gathered for the year's supply of umeboshi "
            "and umeshu, a task that connects households directly to the agricultural calendar."
        ),
        "nature_signs": [
            "Fireflies blink along rice paddies and slow-moving streams after dusk",
            "Fully ripe yellow ume fall from trees; the race to harvest is on",
            "Hydrangeas bloom in full season, their blues and purples deepening with rain",
            "Tsuyu (rainy season) begins in Kyushu and moves northeast across Honshu",
        ],
        "shun_ingredients": [
            {"name_ja": "梅", "name_en": "Ume (Japanese plum)", "note": "Fully ripe for umeboshi and umeshu; the brief window before they fall is the year's most urgent culinary harvest."},
            {"name_ja": "鰹", "name_en": "Katsuo (bonito)", "note": "Strong season; the fish have fed well in warm Kuroshio waters, and the flesh is at peak condition before the return run."},
            {"name_ja": "鰺", "name_en": "Aji (horse mackerel)", "note": "Peak summer season; best for tataki, shioyaki, and nanban-zuke — the most versatile summer fish."},
            {"name_ja": "茄子", "name_en": "Nasu (eggplant)", "note": "First summer eggplant arrives; the skin is tender and flesh dense, ideal for dengaku, miso nasu, and grilling."},
            {"name_ja": "玉葱", "name_en": "Tamanegi (onion)", "note": "New-season Awaji Island onions reach peak; sweet enough to eat raw in paper-thin slices."},
            {"name_ja": "とうもろこし", "name_en": "Tomorokoshi (corn)", "note": "First summer corn from Hokkaido; varieties developed for extreme sweetness, best eaten the day of harvest."},
        ],
        "health_wisdom": (
            "Umeboshi and ume products are the definitive early-summer medicine: citric acid fights fatigue, "
            "alkalizes the body, and kills harmful bacteria in food — essential in the humid, pathogen-friendly rainy season. "
            "Eat one umeboshi with morning rice as traditional shokuiku prescribes."
        ),
        "sakura_recommendations": [
            "Katsuo tataki with fresh garlic, myōga, and Tosa shoyu — the season's most iconic preparation",
            "Nasu dengaku — grilled eggplant with white and red miso glaze, finished with yuzu zest",
        ],
        "haiku": "Plum falls in the rain / the first firefly blinks at dusk / awn and root drink deep",
    },
    {
        "id": "geshi",
        "kanji": "夏至",
        "romaji": "Geshi",
        "english": "Summer Solstice",
        "start_month": 6,
        "start_day": 21,
        "number": 12,
        "description": (
            "The year's longest day arrives during the height of tsuyu rainy season, so the sun's apex is often "
            "experienced as gray and humid rather than brilliantly lit — a characteristically Japanese paradox. "
            "Cicadas begin their sustained summer chorus, a sound so embedded in the culture that its presence "
            "marks the season as unmistakably as any visual cue. "
            "The kitchen must work with the twin demands of abundant ingredients and suppressed appetite: "
            "cold preparations, light textures, and foods that cool from the inside."
        ),
        "nature_signs": [
            "Cicadas begin their sustained drone in earnest across lowland Japan",
            "Tako (octopus) caught in shallow coastal waters reach peak size after spring feeding",
            "Myōga buds push through the soil in garden shade plots",
            "Days are at maximum length; twilight lingers past eight o'clock",
        ],
        "shun_ingredients": [
            {"name_ja": "鰺", "name_en": "Aji (horse mackerel)", "note": "Summer peak; the fat content is highest in June-July, making it ideal for sashimi and tataki."},
            {"name_ja": "蛸", "name_en": "Tako (octopus)", "note": "Summer tako is plump from feeding; Akashi and Hokkaido tako are prized for exceptional tenderness when properly tenderized."},
            {"name_ja": "茗荷", "name_en": "Myōga (Japanese ginger bud)", "note": "The buried shoots emerge just before solstice; sweet-spicy fragrance cools the palate and stimulates appetite lost in heat."},
            {"name_ja": "胡瓜", "name_en": "Kyūri (cucumber)", "note": "Full summer peak; 95% water and at maximum crunch, sliced with salt as the quickest cooling food in the kitchen."},
            {"name_ja": "桃", "name_en": "Momo (peach)", "note": "Yamanashi and Okayama peaches begin ripening; Japanese varieties grown for extraordinary sweetness and perfume over yield."},
            {"name_ja": "ゴーヤ", "name_en": "Gōya (bitter melon)", "note": "Okinawan tradition: the bitter compounds cool metabolism and are believed to reduce summer fatigue at the cellular level."},
        ],
        "health_wisdom": (
            "The solstice is the body's most energetically demanding peak; prioritize hydration above all — "
            "cucumber, watermelon, and cold barley tea replace what sweat takes. "
            "Bitter flavors (gōya, shiso) stimulate digestion when appetite fades in extreme heat."
        ),
        "sakura_recommendations": [
            "Tako and kyūri sunomono — octopus and cucumber in rice vinegar dressing with myōga and wakame",
            "Cold tofu with myōga, katsuobushi, and aged shoyu — summer's simplest and most elegant dish",
        ],
        "haiku": "Long day, short the night / cicadas begin their drone / the sun will not set",
    },
    {
        "id": "shosho",
        "kanji": "小暑",
        "romaji": "Shōsho",
        "english": "Minor Heat",
        "start_month": 7,
        "start_day": 7,
        "number": 13,
        "description": (
            "The heat intensifies with full summer weight: cicadas at maximum volume, pavement shimmering at midday, "
            "yukata-clad figures at evening matsuri seeking momentary relief from the slightest breeze. "
            "This is Doyo — the eighteen-day period of midsummer — and its most celebrated day, Doyo no Ushi no Hi, "
            "is dedicated by tradition to eating unagi (eel) for the stamina needed to survive the heat. "
            "Japanese heat culture has developed a sophisticated culinary vocabulary for endurance."
        ),
        "nature_signs": [
            "Cicadas reach maximum sustained volume across all of lowland Japan",
            "Doyo no ushi no hi brings unagi vendors into even quiet neighborhoods",
            "Evening matsuri lanterns illuminate shrine precincts through humid nights",
            "Edamame pods fill and become plump enough to pop from the shell",
        ],
        "shun_ingredients": [
            {"name_ja": "鰻", "name_en": "Unagi (Japanese eel)", "note": "Doyo no ushi tradition; summer eel fat is at its seasonal peak, providing the concentrated stamina food the heat demands."},
            {"name_ja": "鰺", "name_en": "Aji (horse mackerel)", "note": "Still in prime season; the intensely flavored summer aji makes the best tataki of the year."},
            {"name_ja": "枝豆", "name_en": "Edamame (fresh soybeans)", "note": "Pods fill with sweetness in the summer heat; best eaten within hours of harvest — the sugars convert to starch rapidly."},
            {"name_ja": "西瓜", "name_en": "Suika (watermelon)", "note": "Japanese varieties bred for extreme sweetness and uniform texture; the peak cooling food of midsummer."},
            {"name_ja": "茗荷", "name_en": "Myōga (Japanese ginger bud)", "note": "Full summer peak; the fragrant buds are sliced as a garnish for almost every chilled dish of the season."},
            {"name_ja": "桃", "name_en": "Momo (peach)", "note": "Peak season for Yamanashi Hakuhō and Nagano varieties; eaten cold and peeled as the season's luxury sweet."},
        ],
        "health_wisdom": (
            "Replace minerals lost in sweat with miso soup, pickles, and lightly salted edamame — the traditional "
            "Japanese approach to electrolyte replacement. "
            "Unagi's vitamin B1 and B2 are specifically indicated in traditional shokuiku to combat summer fatigue."
        ),
        "sakura_recommendations": [
            "Unagi kabayaki don with sansho pepper, pickled cucumber, and clear soup — the summer's ritual meal",
            "Chilled aji tataki with myōga, shiso, and cold dashi — eaten over ice to cool the diner from within",
        ],
        "haiku": "Sweat dries on our backs / unagi in lacquer box / a small mercy, cool",
    },
    {
        "id": "taisho",
        "kanji": "大暑",
        "romaji": "Taishō",
        "english": "Major Heat",
        "start_month": 7,
        "start_day": 23,
        "number": 14,
        "description": (
            "Major Heat is the apex of summer's severity: pavement releases stored heat through the night, "
            "and temperatures in the city never fully fall. "
            "Obon arrives — ancestral spirits return, lanterns float on rivers, bon-odori dances circle through "
            "neighborhoods in an atmosphere suspended between celebration and grief. "
            "The kitchen favors the cold: hiyashi chuka, cold tofu, shaved ice, and anything that can be "
            "prepared without additional heat."
        ),
        "nature_signs": [
            "Obon lanterns float on rivers throughout the country",
            "Awabi (abalone) are at peak size after summer feeding on kelp forests",
            "Sazae (turban shells) crowd onto coastal rocks; beach tsubo-yaki vendors appear",
            "Sunflower fields reach full height and bloom across rural Japan",
        ],
        "shun_ingredients": [
            {"name_ja": "鰻", "name_en": "Unagi (Japanese eel)", "note": "Continued peak; the second round of Doyo no ushi no hi falls in this period for many years."},
            {"name_ja": "鮑", "name_en": "Awabi (abalone)", "note": "Summer awabi feed on abundant kelp, producing rich, firm flesh; the liver sauce (kimo) is a distinct seasonal delicacy."},
            {"name_ja": "栄螺", "name_en": "Sazae (turban shell)", "note": "Tsubo-yaki — grilled in the shell with sake and butter — is the unmistakable taste of a Japanese summer festival."},
            {"name_ja": "枝豆", "name_en": "Edamame (fresh soybeans)", "note": "Deep summer peak; Daitokuji and Chacha varieties in Kyoto and Hokkaido at their sweetest."},
            {"name_ja": "ゴーヤ", "name_en": "Gōya (bitter melon)", "note": "Okinawan champuru tradition; paired with tofu and egg, the bitterness becomes the season's most honest flavor."},
            {"name_ja": "胡瓜", "name_en": "Kyūri (cucumber)", "note": "Maximum summer abundance; eaten sliced with miso as a cooling snack throughout the day."},
        ],
        "health_wisdom": (
            "The body's energy is most depleted during Taishō; prioritize sleep, reduce physical exertion midday, "
            "and eat smaller meals more frequently to avoid burdening a heat-stressed digestion. "
            "Gōya's bitter compounds are scientifically validated to support insulin function under heat stress."
        ),
        "sakura_recommendations": [
            "Awabi sashimi with liver sauce and fresh wasabi — the luxury centerpiece of a summer omakase",
            "Sazae tsubo-yaki — turban shells grilled at the table with sake, soy, and summer herbs",
        ],
        "haiku": "The city shimmers / even the sea holds its heat / ice cracks in the glass",
    },
    {
        "id": "risshu",
        "kanji": "立秋",
        "romaji": "Risshū",
        "english": "Start of Autumn",
        "start_month": 8,
        "start_day": 7,
        "number": 15,
        "description": (
            "Autumn arrives by name while the thermometer still reads summer — this gap between the declared "
            "and the felt gives Risshū its characteristic tension. "
            "Look carefully and the evidence accumulates: dragonflies appear in numbers, late-afternoon light "
            "acquires its first faint amber tint, and the earliest sanma (Pacific saury) arrive in northern markets. "
            "This period rewards the cook who can sense the shift before it becomes visible."
        ),
        "nature_signs": [
            "Dragonflies appear suddenly in large numbers over paddies and rivers",
            "Sanma (Pacific saury) detected in northern Hokkaido waters — the first signal of autumn fish",
            "The quality of late-afternoon light begins its slow shift toward gold",
            "Morning glory flowers peak on garden fences as summer's final exuberance",
        ],
        "shun_ingredients": [
            {"name_ja": "秋刀魚", "name_en": "Sanma (Pacific saury)", "note": "Just arriving from the northern Pacific; the first sanma of autumn are fatty and command premium prices even before their full peak."},
            {"name_ja": "鰹", "name_en": "Modori-gatsuo (returning bonito)", "note": "The southward-migrating fall bonito has fed all summer and is far fattier than the spring run — the year's richest katsuo."},
            {"name_ja": "とうもろこし", "name_en": "Tomorokoshi (corn)", "note": "Hokkaido peak; the brief northern summer concentrates sweetness into extraordinary varieties like Yūmeru and Pirika."},
            {"name_ja": "茄子", "name_en": "Nasu (eggplant)", "note": "Summer's last abundant eggplant before the heat fades; folklore says autumn nasu should not be given to daughters-in-law, being too delicious."},
            {"name_ja": "梨", "name_en": "Nashi (Japanese pear)", "note": "New-season pears arrive; Kōsui and Nijisseiki varieties are crisp, refreshing, and carry summer sweetness into the first cool days."},
            {"name_ja": "無花果", "name_en": "Ichijiku (fig)", "note": "Summer figs begin to ripen; deep purple skin with honey-sweet red interior, best eaten slightly chilled as is."},
        ],
        "health_wisdom": (
            "Begin transitioning from purely cooling foods toward those that also nourish the lungs, "
            "which traditional Japanese medicine associates with autumn: pear, white foods, and moderate warming spices. "
            "The modori-gatsuo's fat is the ideal autumn food — rich enough to begin building reserves for winter."
        ),
        "sakura_recommendations": [
            "First sanma shioyaki — Pacific saury salt-grilled whole with grated daikon, sudachi, and soy",
            "Modori-gatsuo tataki — autumn's fattiest bonito with ginger, garlic, and Tosa shoyu",
        ],
        "haiku": "Autumn in the name / but heat still rests on our backs / the dragonfly knows",
    },
    {
        "id": "shosho_end",
        "kanji": "処暑",
        "romaji": "Shosho",
        "english": "End of Heat",
        "start_month": 8,
        "start_day": 23,
        "number": 16,
        "description": (
            "The kanji declares it plainly: heat handled, heat dealt with, heat on its way out. "
            "Mornings and evenings become genuinely cool, startling after months of unbroken warmth, "
            "and the cicadas' cry grows hoarse and intermittent before eventually falling silent. "
            "New rice harvests begin in early-ripening southern regions, and the kitchen begins "
            "welcoming the first autumn foods that signal recovery and preparation."
        ),
        "nature_signs": [
            "Cicada chorus grows sparse and ragged as adults reach end of life",
            "First cool mornings arrive; dew appears on grass before sunrise",
            "Early-harvest regions in Kyushu begin cutting rice in late August",
            "Wild grapes ripen in mountain clearings; bears begin their pre-hibernation feeding",
        ],
        "shun_ingredients": [
            {"name_ja": "秋刀魚", "name_en": "Sanma (Pacific saury)", "note": "Season accelerating toward peak; fat content rising weekly as the fish feed in rich northern Pacific waters."},
            {"name_ja": "鰹", "name_en": "Modori-gatsuo (returning bonito)", "note": "Peak of the fat autumn bonito run; the richest, most satisfying katsuo of the year, best as tataki or sashimi."},
            {"name_ja": "新米", "name_en": "Shinmai (new rice)", "note": "Early-harvest new rice carries a milky fragrance when cooked that aged rice can never replicate; served plain to honor it."},
            {"name_ja": "無花果", "name_en": "Ichijiku (fig)", "note": "Peak fig season; Masui Dauphine and Houraishi varieties with jammy interior and papery skin."},
            {"name_ja": "葡萄", "name_en": "Budō (grape)", "note": "Kyoho and Pione grapes enter prime season; the thick skins slip off to reveal jammy, perfumed flesh grown for flavor, not transport."},
            {"name_ja": "茗荷", "name_en": "Myōga (Japanese ginger bud)", "note": "Late summer final burst; the fragrant buds are still excellent, sweeter now than at solstice peak."},
        ],
        "health_wisdom": (
            "The body exhales after summer's long effort; nourish the transition with new rice, "
            "ripe fruit, and the fat of modori-gatsuo to begin rebuilding reserves for the cooler months. "
            "Reduce cold foods gradually and reintroduce warming soups as morning temperatures drop."
        ),
        "sakura_recommendations": [
            "Shinmai gohan set — new rice served plain with three pickles and miso soup to honor the harvest",
            "Modori-gatsuo no tataki — autumn bonito with myōga, ponzu, and sudachi as the season's farewell to summer fish",
        ],
        "haiku": "Morning air has changed / the cicada's cry is hoarse / new rice waits in fields",
    },
    {
        "id": "hakuro",
        "kanji": "白露",
        "romaji": "Hakuro",
        "english": "White Dew",
        "start_month": 9,
        "start_day": 8,
        "number": 17,
        "description": (
            "Morning dew sparkles on the grass before evaporating into a day still warm enough for shirtsleeves — "
            "the characteristic contrast of early autumn. "
            "Sanma arrive in earnest from the north, silver and plump, their fat content rising with each "
            "passing week as they feed before winter. "
            "The matsutake mushroom emerges in red pine forests after autumn rains, its incense-like fragrance "
            "so specific and evocative that no translation fully captures it."
        ),
        "nature_signs": [
            "White dew crystallizes on tall grasses before dawn, evaporating by midmorning",
            "Sanma boats return loaded from the Sanriku and Hokkaido coasts",
            "Matsutake emerge in red pine forests after the first cool rains",
            "Cosmos flowers bloom in pink and white drifts along country roadsides",
        ],
        "shun_ingredients": [
            {"name_ja": "秋刀魚", "name_en": "Sanma (Pacific saury)", "note": "Absolute seasonal peak; fat content now highest, the fish are heavy and silver-bright, best simply salt-grilled."},
            {"name_ja": "松茸", "name_en": "Matsutake (pine mushroom)", "note": "Japan's most prized mushroom; the irreplaceable incense-pine fragrance emerges only after cool autumn rains in old-growth pine forest."},
            {"name_ja": "栗", "name_en": "Kuri (chestnut)", "note": "First chestnuts of the year arrive; Tamba kuri from Kyoto is considered the finest, used in kurigohan and wagashi."},
            {"name_ja": "葡萄", "name_en": "Budō (grape)", "note": "Full peak; Muscat Bailey A and Pione grapes at maximum fragrance and sweetness."},
            {"name_ja": "さつまいも", "name_en": "Satsumaimo (sweet potato)", "note": "Sugar develops as cool nights lengthen; baked in embers, the skin caramelizes and the flesh becomes like custard."},
            {"name_ja": "蕪", "name_en": "Kabu (turnip)", "note": "Autumn turnips are denser and sweeter than spring; braised in light dashi they become almost translucent."},
        ],
        "health_wisdom": (
            "Autumn is the season to nourish the lungs according to traditional Japanese medicine; "
            "pear, white sesame, and lily bulb (yurine) are the classic lung-moistening foods as dry air arrives. "
            "Chestnut provides concentrated mineral nutrition to begin building winter reserves."
        ),
        "sakura_recommendations": [
            "Matsutake dobin-mushi — pine mushroom and ginkgo nut steamed in dashi broth, the season's most elegant soup",
            "Sanma shioyaki with momiji oroshi and sudachi — the definitive autumn preparation",
        ],
        "haiku": "Dew beads on tall grass / moonlight catches what is there / the world has grown still",
    },
    {
        "id": "shubun",
        "kanji": "秋分",
        "romaji": "Shūbun",
        "english": "Autumn Equinox",
        "start_month": 9,
        "start_day": 23,
        "number": 18,
        "description": (
            "The autumn equinox returns day and night to perfect balance before the year tips decisively toward darkness. "
            "This is Ohigan again — the Buddhist period of ancestor veneration — and the rice harvest enters its main "
            "season: fields that were vivid green are now heavy-headed and golden. "
            "The harvest moon is celebrated with pampas grass and tsukimi dango, a moment of abundance before "
            "the discipline of winter begins."
        ),
        "nature_signs": [
            "Rice fields turn golden as main-crop harvest begins across Honshu",
            "The harvest moon rises enormous and orange above harvest fields",
            "Colchicum and red spider lily blooms appear along rice paddy banks",
            "Persimmons turn orange on trees stripped of leaves in the first autumn gales",
        ],
        "shun_ingredients": [
            {"name_ja": "松茸", "name_en": "Matsutake (pine mushroom)", "note": "Full peak season; the window is brief and the fragrance is at its most intense in the two weeks around the equinox."},
            {"name_ja": "栗", "name_en": "Kuri (chestnut)", "note": "Prime season; chestnuts scored and roasted, or peeled for kurigohan — the taste of autumn harvest."},
            {"name_ja": "柿", "name_en": "Kaki (persimmon)", "note": "Harvest moon fruit; Hachiya and Fuyu varieties sweeten dramatically after cool nights begin in earnest."},
            {"name_ja": "新米", "name_en": "Shinmai (new rice)", "note": "Main-crop new rice now widely available; the fresh-milled fragrance and soft texture reward eating with simple accompaniments."},
            {"name_ja": "秋刀魚", "name_en": "Sanma (Pacific saury)", "note": "Still prime and deeply fat; the last weeks of peak sanma before they begin their southward retreat."},
            {"name_ja": "さつまいも", "name_en": "Satsumaimo (sweet potato)", "note": "Harvest peak across the country; Naruto Kintoki from Tokushima and Beniazuma from Ibaraki at their finest."},
        ],
        "health_wisdom": (
            "Eat new rice, chestnuts, and root vegetables to rebuild what summer heat depleted — these are "
            "the densely nutritious autumn 'tonic foods' (yakuzen) of Japanese dietary tradition. "
            "The equinox marks the body's pivot toward warmth-retention; begin adding miso and warming spices "
            "to daily meals."
        ),
        "sakura_recommendations": [
            "Matsutake gohan — rice cooked with fresh matsutake and dashi, finished with sea salt and mitsuba",
            "Sanma tataki with autumn herbs and persimmon vinegar dressing — a farewell to the season's great fish",
        ],
        "haiku": "Equal dark and light / the harvest moon hangs exact / autumn holds the scales",
    },
    {
        "id": "kanro",
        "kanji": "寒露",
        "romaji": "Kanro",
        "english": "Cold Dew",
        "start_month": 10,
        "start_day": 8,
        "number": 19,
        "description": (
            "Dew turns cold on the edges of turning maple leaves, and some mornings show a crystalline "
            "fringe that is almost frost. "
            "Salmon have entered rivers for their spawning runs, and the roe swells with fat that makes ikura "
            "one of Japan's most treasured seasonal foods. "
            "The Japanese word monono aware — the pathos of things — is most perfectly felt in October, "
            "when beauty is inseparable from transience."
        ),
        "nature_signs": [
            "Red and gold maples begin their peak color transformation",
            "Salmon are visible in clear rivers, pushing upstream with tremendous effort",
            "Geese and crane formations cross the sky in large southward formations",
            "Yellowing ginkgo trees line temple avenues; the first nuts fall",
        ],
        "shun_ingredients": [
            {"name_ja": "鰤", "name_en": "Buri (young yellowtail/hamachi)", "note": "Beginning its southward migration; fat content builds week by week as the fish feed for winter."},
            {"name_ja": "鮭", "name_en": "Sake (salmon)", "note": "Pacific salmon in peak spawning run; deep orange flesh swollen with oil accumulated through a summer of feeding."},
            {"name_ja": "イクラ", "name_en": "Ikura (salmon roe)", "note": "The roe bulges with fat and flavor as salmon prepare to spawn; ikura donburi is the quintessential autumn dish."},
            {"name_ja": "松茸", "name_en": "Matsutake (pine mushroom)", "note": "Season closing in warmer regions; remaining matsutake develop the deepest, most mature fragrance."},
            {"name_ja": "蓮根", "name_en": "Renkon (lotus root)", "note": "Autumn renkon has fully developed starch; the crisp texture and mild sweetness shine in kinpira, tempura, and nimono."},
            {"name_ja": "柿", "name_en": "Kaki (persimmon)", "note": "Full season; dried hoshigaki hanging from farmhouse eaves begin their month-long transformation to amber sweetness."},
        ],
        "health_wisdom": (
            "Salmon and ikura provide the omega-3 fatty acids and astaxanthin that traditional Japanese medicine "
            "associates with fortifying the blood and warming the extremities as cold increases. "
            "Root vegetables now appear at every meal to ground and center the body through the seasonal transition."
        ),
        "sakura_recommendations": [
            "Ikura and shinmai donburi — salmon roe over new rice with seaweed, wasabi, and dashi-dipped nori",
            "Salmon nanban-zuke with renkon and autumn vegetables in sweet rice vinegar",
        ],
        "haiku": "Dew turns cold on leaves / the salmon begin their run / first fires of the fall",
    },
    {
        "id": "soko",
        "kanji": "霜降",
        "romaji": "Sōkō",
        "english": "Frost's Descent",
        "start_month": 10,
        "start_day": 23,
        "number": 20,
        "description": (
            "Frost descends on the persimmons and what the cold takes in color it returns in sweetness — "
            "the tannins that made them astringent break down with the chill, converting to honey. "
            "Ginkgo and maple reach their blazing climax; oysters, dormant through the warm months, "
            "have quietly built their fat reserves and return to the table. "
            "The kitchen enters a mode of richly purposeful preservation: yuzu is zested, burdock scrubbed "
            "for simmering, and the year's last outdoor abundance carefully honored."
        ),
        "nature_signs": [
            "First frosts arrive on highland plateaus and northern valleys",
            "Forest foliage reaches peak color from Tohoku south to the Kii Peninsula",
            "Oyster farming operations begin harvesting the season's first fat oysters",
            "Bears intensify pre-hibernation feeding in mountain forests",
        ],
        "shun_ingredients": [
            {"name_ja": "鰤", "name_en": "Buri (yellowtail)", "note": "Fattening steadily as it moves south; by November this will be 'kan-buri' but the October fish already has excellent fat."},
            {"name_ja": "牡蠣", "name_en": "Kaki (oyster)", "note": "Cold water returns and oysters have spent autumn feeding; the first October oysters are creamy and briny-sweet."},
            {"name_ja": "柚子", "name_en": "Yuzu (yuzu citrus)", "note": "The bright yellow citrus begins ripening; the aromatic oils in the skin are now the most versatile and fragrant seasoning of autumn."},
            {"name_ja": "牛蒡", "name_en": "Gobō (burdock root)", "note": "Peak maturity; the deep earthy mineral flavors ideal for kinpira, mixed rice, and long braises."},
            {"name_ja": "りんご", "name_en": "Ringo (apple)", "note": "Aomori Fuji apples reach peak after the first frosts; exceptional for eating fresh and for dessert applications."},
            {"name_ja": "柿", "name_en": "Kaki (persimmon)", "note": "Full season; frost-sweetened persimmons are now at their most complex and enjoyable."},
        ],
        "health_wisdom": (
            "The body needs warming, circulating foods now: yuzu, ginger, and burdock all support peripheral "
            "circulation as the first frosts chill the extremities. "
            "Begin supplementing with roasted sesame and walnuts to nourish the kidneys for the winter ahead."
        ),
        "sakura_recommendations": [
            "Oyster dobin-mushi with yuzu and early matsutake — autumn's richest warming soup",
            "Buri daikon — yellowtail and white radish braised in sweet soy with grated ginger and yuzu peel",
        ],
        "haiku": "First frost on the leaf / persimmon sweetens with cold / the crow understands",
    },
    {
        "id": "ritto",
        "kanji": "立冬",
        "romaji": "Rittō",
        "english": "Start of Winter",
        "start_month": 11,
        "start_day": 7,
        "number": 21,
        "description": (
            "Winter is official, though the southern half of Japan may still be mild while Hokkaido sits under early snow. "
            "The yellowtail has entered the category of 'kan-buri' — cold-water yellowtail — a designation "
            "that indicates premium quality and triggers celebrations in the coastal fishing towns of Toyama and Ishikawa. "
            "Root vegetables consolidate their role as the kitchen's foundation; nabe pots appear on tables "
            "as winter's version of hospitality — deep, still, and sustaining."
        ),
        "nature_signs": [
            "First snows dust the peaks of the Japan Alps and northern ranges",
            "Kan-buri fishing fleets deploy from Himi and Toyama Bay ports",
            "Fallen leaves carpet shrine paths; raking begins in earnest",
            "Winter constellations appear in the eastern sky after dusk",
        ],
        "shun_ingredients": [
            {"name_ja": "鰤", "name_en": "Kan-buri (cold-water yellowtail)", "note": "Entering the premium 'cold yellowtail' category; sashimi flesh shows visible white marbling of fat."},
            {"name_ja": "牡蠣", "name_en": "Kaki (oyster)", "note": "November oysters have built considerable fat; Hiroshima and Munakata varieties at prime condition for both raw and cooked preparations."},
            {"name_ja": "鱈", "name_en": "Tara (Pacific cod)", "note": "Cod season begins with white, flaking flesh and the prized white shirako (milt) — a winter delicacy available only now."},
            {"name_ja": "大根", "name_en": "Daikon (white radish)", "note": "Autumn daikon grown slow in cooling soil is milder and sweeter than summer; ideal for long simmering and oden."},
            {"name_ja": "白菜", "name_en": "Hakusai (napa cabbage)", "note": "Tightly heading with the cold; the winter hakusai's dense sweetness is essential for nabe and pickled kimchi-style preparations."},
            {"name_ja": "柚子", "name_en": "Yuzu", "note": "Peak fragrance for the entire season; the zest and juice elevate virtually every winter preparation."},
        ],
        "health_wisdom": (
            "Winter calls for dense, warming foods that build and maintain internal heat: fatty fish, root vegetables "
            "in rich dashi, and miso-based preparations. "
            "Avoid the refrigerator-cold drinks that remain habit from summer; everything consumed now should "
            "be warm or room temperature."
        ),
        "sakura_recommendations": [
            "Kan-buri sashimi platter — thick-cut yellowtail with tosa shoyu, ginger, and sliced negi",
            "Tara to hakusai no nabe — cod and napa cabbage hot pot with yuzu ponzu for dipping",
        ],
        "haiku": "The hearth is relit / yellowtail swims in cold brine / winter is our home",
    },
    {
        "id": "shosetsu",
        "kanji": "小雪",
        "romaji": "Shōsetsu",
        "english": "Minor Snow",
        "start_month": 11,
        "start_day": 22,
        "number": 22,
        "description": (
            "Light snow dusts the mountain peaks of the north and the Sea of Japan coast settles under "
            "the gray skies it will wear for months. "
            "Monkfish (ankō) reaches its prime, and the prized liver — ankimo — is considered among Japan's "
            "great winter delicacies, often compared to foie gras in its richness and complexity. "
            "Yuzu, at the height of its aromatic season, appears in everything: baths, ponzu, clear soups, "
            "and pressed over winter tofu."
        ),
        "nature_signs": [
            "Light snow falls on mountain peaks visible from cities on the Sea of Japan coast",
            "Nabe (hot pot) season begins in earnest in households across Japan",
            "Monkfish deliveries increase at coastal markets in Ibaraki and Fukushima",
            "Year-end osechi preparations begin in traditional households",
        ],
        "shun_ingredients": [
            {"name_ja": "あんこう", "name_en": "Ankō (monkfish)", "note": "Peak season; the entire fish is used — the liver (ankimo) is the richest winter delicacy, served warm with ponzu."},
            {"name_ja": "鰤", "name_en": "Kan-buri (cold-water yellowtail)", "note": "Building toward its January peak; the fat content is extraordinary, the flesh dense and luxuriously marbled."},
            {"name_ja": "鱈", "name_en": "Tara (Pacific cod)", "note": "Full season; shirako (cod milt) available in abundance, served warm with citrus ponzu as an umami-dense winter starter."},
            {"name_ja": "柚子", "name_en": "Yuzu", "note": "At absolute peak of skin fragrance; the essential oils in the zest are most aromatic in cold weather — used in everything."},
            {"name_ja": "蕪", "name_en": "Kabu (turnip)", "note": "November turnips are fat and sweet from slow cold growth; braised in light dashi and finished with yuzu they are deeply comforting."},
            {"name_ja": "長葱", "name_en": "Negi (Japanese leek)", "note": "Winter negi at peak; frost converts outer layers to sweet aromatic gel, making the white part silky and prized."},
        ],
        "health_wisdom": (
            "Ankimo (monkfish liver) is one of the ocean's most concentrated sources of vitamins D and B12 — "
            "both critical in the dark months when sun exposure drops. "
            "Warm miso soup with yuzu zest morning and evening supports circulation through the coldest weeks."
        ),
        "sakura_recommendations": [
            "Ankō nabe with ankimo miso — monkfish hot pot finished with the liver beaten into miso at the table",
            "Tara shirako ponzu — fresh cod milt served warm with yuzu ponzu and momiji oroshi",
        ],
        "haiku": "Fine snow on the sill / nabe bubbles on the stove / silence fills the room",
    },
    {
        "id": "taisetsu",
        "kanji": "大雪",
        "romaji": "Taisetsu",
        "english": "Major Snow",
        "start_month": 12,
        "start_day": 7,
        "number": 23,
        "description": (
            "Heavy snowfall arrives in earnest across the mountains and the Sea of Japan coast, "
            "and even cities that rarely see snow may wake to white silence. "
            "Bears have entered hibernation, rivers slow under forming ice, and the year's energy retreats "
            "to its minimum — what grows now grows underground, without fanfare. "
            "Yellowtail fishermen on the Sea of Japan coast prepare their nets for the kan-buri season "
            "that will be celebrated with lavish sashimi platters from Toyama to Kanazawa."
        ),
        "nature_signs": [
            "Heavy snowfall covers the Sea of Japan coast and mountain regions",
            "Bears enter final hibernation; only tracks in fresh snow remain",
            "Kan-buri fishing peaks off Himi, Toyama, as the fish school near the warmer bottom current",
            "Yuzu orchards are harvested in Kochi and Tokushima before the year ends",
        ],
        "shun_ingredients": [
            {"name_ja": "鰤", "name_en": "Kan-buri (cold-water yellowtail)", "note": "Approaching absolute peak; the fish schooling in the cold Sea of Japan develop fat content that justifies 'king of winter fish.'"},
            {"name_ja": "鱈", "name_en": "Tara (Pacific cod)", "note": "Full season prime; the white flesh and abundant shirako make December cod the central ingredient of winter nabe."},
            {"name_ja": "あんこう", "name_en": "Ankō (monkfish)", "note": "Peak liver season; the cold waters of the northern Pacific produce ankimo of unsurpassed richness and delicacy."},
            {"name_ja": "白菜", "name_en": "Hakusai (napa cabbage)", "note": "Freeze-thaw cycles in the field concentrate the sugars; December hakusai is sweeter than any other month."},
            {"name_ja": "柚子", "name_en": "Yuzu", "note": "Peak of the season; aromatic oils are most intense in cold, and the entire fruit — skin, juice, pith — finds use in winter cooking."},
            {"name_ja": "昆布", "name_en": "Kombu (kelp)", "note": "Premium Rishiri and Rausu kombu best deployed in winter when the complexity of dashi is most needed against the season's richness."},
        ],
        "health_wisdom": (
            "December is the time for osechi preparation: the concentrated, preserved foods of the new year feast "
            "are rooted in shokuiku wisdom about building reserves and honoring the year's abundance. "
            "Eat densely and warmly; this is not a time for dietary restraint."
        ),
        "sakura_recommendations": [
            "Kan-buri sashimi three ways — plain, with ponzu, and with tosa joyu — to honor the season's finest fish",
            "Tara nabe with kombu dashi, ankimo miso, and hakusai — winter's most warming communal dish",
        ],
        "haiku": "Heavy snow on branch / the river stiffens with cold / yellowtail runs deep",
    },
    {
        "id": "toji",
        "kanji": "冬至",
        "romaji": "Tōji",
        "english": "Winter Solstice",
        "start_month": 12,
        "start_day": 22,
        "number": 24,
        "description": (
            "The shortest day and the longest night: after this hinge point, each passing day returns "
            "a small portion of light, and Tōji is understood in Japan not as the depth of winter "
            "but as the promise of spring's eventual return. "
            "Traditional practice prescribes the yuzu bath — whole yuzu floated in the ofuro — releasing "
            "skin oils that warm the body, calm the spirit, and are believed to ward off winter illness. "
            "Kabocha squash is the Tōji food, eaten for health and the round shape's association with "
            "good fortune; its dense sweetness provides maximum warmth at the year's coldest moment."
        ),
        "nature_signs": [
            "The year's shortest day; twilight begins before five o'clock across all of Japan",
            "Yuzu orchards glow yellow against bare winter trees in Kochi prefecture",
            "Ice forms nightly on ponds and slow rivers; mornings are silent",
            "Winter birds — waxwings, fieldfares — arrive from the continent in flocks",
        ],
        "shun_ingredients": [
            {"name_ja": "河豚", "name_en": "Fugu (blowfish)", "note": "The most prized winter delicacy; cold water produces the firmest, cleanest white flesh, best as thin sashimi (tessa) or in chiri nabe."},
            {"name_ja": "鱈", "name_en": "Tara (Pacific cod)", "note": "Peak season; Japanese tradition holds that eating daikon and tara on the solstice prevents illness through the remainder of winter."},
            {"name_ja": "鰤", "name_en": "Kan-buri (cold-water yellowtail)", "note": "At absolute peak fat content for the entire year; the celebration fish of the Sea of Japan winter season."},
            {"name_ja": "南瓜", "name_en": "Kabocha (Japanese pumpkin)", "note": "Traditional Tōji food; stored kabocha develops concentrated sweetness believed to fortify the body against winter illness."},
            {"name_ja": "柚子", "name_en": "Yuzu", "note": "The Tōji yuzu bath (yuzu-yu) warms and protects; the juice and zest also brighten white fish and enrich winter miso."},
            {"name_ja": "大根", "name_en": "Daikon (white radish)", "note": "The 'round food' tradition of Tōji includes daikon; slowly simmered in rich broth it becomes translucent and deeply comforting."},
        ],
        "health_wisdom": (
            "The solstice is the year's energetic nadir; sleep longer, eat warming foods at every meal, "
            "and take the yuzu bath as traditional medicine prescribes — the skin absorbs the oils directly. "
            "Kabocha provides beta-carotene and complex carbohydrates for sustained warmth through the longest night."
        ),
        "sakura_recommendations": [
            "Kabocha nimono — winter squash simmered in sweet dashi with yuzu peel and a scattering of black sesame",
            "Fugu chiri nabe with ponzu, green onion, and momiji oroshi — the year's most celebratory winter dish",
        ],
        "haiku": "The year's shortest day / yuzu floats in the hot bath / from here light returns",
    },
]


def get_current_sekki(month: int, day: int) -> dict:
    """Return the sekki active on the given month/day.

    Iterates through SEKKI (ordered Jan 5 through Dec 22) and returns
    the last entry whose start date falls on or before the given date.
    If the date is before Jan 5 (i.e., Jan 1–4), Tōji from the previous
    year is still active, so SEKKI[-1] (Tōji, Dec 22) is returned.

    Args:
        month: Calendar month as an integer (1=January, 12=December).
        day:   Calendar day as an integer.

    Returns:
        The matching sekki dict from SEKKI.

    Examples:
        >>> get_current_sekki(1, 5)["id"]
        'shokan'
        >>> get_current_sekki(1, 3)["id"]   # before Shōkan; wraps to Tōji
        'toji'
        >>> get_current_sekki(12, 22)["id"]
        'toji'
        >>> get_current_sekki(4, 10)["id"]  # between Seimei (Apr 5) and Kokuu (Apr 20)
        'seimei'
    """
    current = (month, day)
    active = None
    for sekki in SEKKI:
        start = (sekki["start_month"], sekki["start_day"])
        if start <= current:
            active = sekki
    # Dates before Jan 5 fall within Tōji of the previous year.
    if active is None:
        active = SEKKI[-1]
    return active
