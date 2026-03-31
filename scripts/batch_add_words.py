#!/usr/bin/env python3
"""批量添加单词到词库"""
import os
from datetime import datetime

BASE_DIR = "/Users/raymond.zhong/Desktop/EN_Learning_OC"
WORDS_FILE = os.path.join(BASE_DIR, "vocabulary", "words.md")
LOG_FILE = os.path.join(BASE_DIR, "query_log.md")
TODAY = datetime.now().strftime("%Y-%m-%d")

# 已存在的词（跳过）
EXISTING = {"moderate", "simulate", "illuminate", "despite", "maven", "nostalgic", "thrilled"}

# 新单词列表：(word, phonetic, pos_and_meanings, example_en, example_cn)
NEW_WORDS = [
    ("thrill", "/θrɪl/", "n. 兴奋；激动；震颤感\nv. 使非常兴奋；使非常激动",
     "The roller coaster gave me a real thrill.", "过山车给了我一种真正的兴奋感。"),
    ("tailor", "/ˈteɪlər/", "v. 专门制作；定做\nn. （尤指定制男装的）裁缝",
     "We can tailor the program to your specific needs.", "我们可以根据你的具体需求定制这个方案。"),
    ("gem", "/dʒem/", "n. 宝石；难能可贵的人；美妙绝伦的事物\nv. 用宝石装饰",
     "This little restaurant is a real gem.", "这家小餐馆真是个难得的好地方。"),
    ("recipes", "/ˈresəpiz/", "n. 食谱；配方；秘诀",
     "She shared her family recipes with me.", "她和我分享了她家的食谱。"),
    ("genie", "/ˈdʒiːni/", "n. 精灵（尤指阿拉伯故事中的）",
     "The genie granted him three wishes.", "精灵给了他三个愿望。"),
    ("consumers", "/kənˈsuːmərz/", "n. 消费者（consumer的复数）",
     "Consumers are becoming more aware of their rights.", "消费者越来越意识到自己的权利。"),
    ("orient", "/ˈɔːrient/", "v. 适应；使朝向；确定方向\nn. 东方；远东",
     "It took him a while to orient himself in the new city.", "他花了一段时间才在新城市中找到方向。"),
    ("disaster", "/dɪˈzæstər/", "n. 灾害；灾难；灾祸；不幸",
     "The earthquake was a major disaster for the region.", "地震对这个地区是一场重大灾难。"),
    ("genuinely", "/ˈdʒenjuɪnli/", "adv. 由衷地；真诚地；真正地",
     "She was genuinely surprised by the gift.", "她对这份礼物感到由衷的惊喜。"),
    ("authentic", "/ɔːˈθentɪk/", "adj. 真正的；真品的；真实的；地道的",
     "This restaurant serves authentic Italian food.", "这家餐厅供应正宗的意大利菜。"),
    ("amateur", "/ˈæmətʃər/", "n. 业余爱好者；生手；外行\nadj. 业余的",
     "He's an amateur photographer with a lot of talent.", "他是一个很有天赋的业余摄影师。"),
    ("framework", "/ˈfreɪmwɜːrk/", "n. 框架；机制；准则",
     "We need a clear framework for making decisions.", "我们需要一个清晰的决策框架。"),
    ("consumer", "/kənˈsuːmər/", "n. 消费者；用户",
     "Consumer spending has increased this quarter.", "本季度消费者支出有所增加。"),
    ("commercial", "/kəˈmɜːrʃl/", "adj. 商业的；贸易的；赢利的\nn. 广告",
     "The company launched a new commercial on TV.", "公司在电视上投放了一则新广告。"),
    ("orchestrator", "/ˈɔːrkɪstreɪtər/", "n. 管弦乐编曲者；策划者；协调者",
     "She was the orchestrator of the entire event.", "她是整个活动的策划者。"),
    ("acquisition", "/ˌækwɪˈzɪʃn/", "n. 收购；获得；购得物",
     "The acquisition of the company cost $2 billion.", "收购这家公司花了20亿美元。"),
    ("hype", "/haɪp/", "n. 大肆宣传；炒作\nv. 夸张地宣传",
     "Don't believe the hype—the product isn't that great.", "别相信那些炒作——产品没有那么好。"),
    ("customize", "/ˈkʌstəmaɪz/", "v. 定制；自定义",
     "You can customize the settings to suit your preferences.", "你可以自定义设置以适合你的偏好。"),
    ("dynamic", "/daɪˈnæmɪk/", "adj. 充满活力的；不断变化的\nn. 动力；动力学",
     "The city has a dynamic and exciting atmosphere.", "这座城市有一种充满活力和令人兴奋的氛围。"),
    ("discourse", "/ˈdɪskɔːrs/", "n. 话语；语篇；论文\nv. 谈；讲演",
     "Public discourse on climate change has intensified.", "关于气候变化的公共讨论已经加剧。"),
    ("portray", "/pɔːrˈtreɪ/", "v. 描绘；描写；将…描写成；扮演",
     "The movie portrays life in rural China.", "这部电影描绘了中国农村的生活。"),
    ("stereotype", "/ˈsteriətaɪp/", "n. 刻板印象；模式化观念\nv. 对…形成模式化看法",
     "We should challenge stereotypes rather than accept them.", "我们应该挑战刻板印象而不是接受它们。"),
    ("amplifies", "/ˈæmplɪfaɪz/", "v. 放大；详述；增强（amplify的三单）",
     "Social media amplifies both good and bad information.", "社交媒体放大了好的和坏的信息。"),
    ("randomly", "/ˈrændəmli/", "adv. 随机地；随意地",
     "The names were randomly selected from a list.", "名字是从列表中随机选出的。"),
    ("violation", "/ˌvaɪəˈleɪʃn/", "n. 违反；侵犯；违背",
     "This is a clear violation of the rules.", "这是对规则的明显违反。"),
    ("penalty", "/ˈpenəlti/", "n. 处罚；刑罚；罚款；点球",
     "The penalty for speeding can be a heavy fine.", "超速的处罚可以是一笔巨额罚款。"),
    ("opt out of", "", "phr. 选择退出；决定不参加",
     "You can opt out of the email subscription at any time.", "你可以随时选择退出电子邮件订阅。"),
    ("third parties", "", "n. 第三方",
     "We do not share your data with third parties.", "我们不会与第三方分享你的数据。"),
    ("pharmaceutical", "/ˌfɑːrməˈsuːtɪkl/", "adj. 制药的；配药的\nn. 药物",
     "The pharmaceutical industry invests billions in research.", "制药行业在研究上投入了数十亿。"),
    ("perpetuity", "/ˌpɜːrpəˈtuːəti/", "n. 永久；永恒；永续年金",
     "The land was granted to them in perpetuity.", "这块土地被永久地授予了他们。"),
    ("consent", "/kənˈsent/", "n. 同意；允许；赞同\nv. 同意；准许",
     "You need parental consent to go on the school trip.", "你需要父母的同意才能参加学校旅行。"),
    ("inevitable", "/ɪnˈevɪtəbl/", "adj. 不可避免的；必然的\nn. 不可避免的事",
     "Change is inevitable in any organization.", "在任何组织中变化都是不可避免的。"),
    ("slightly", "/ˈslaɪtli/", "adv. 稍微；略微",
     "The price has increased slightly this month.", "这个月价格略有上涨。"),
    ("misrepresentation", "/ˌmɪsˌreprɪzenˈteɪʃn/", "n. 歪曲；误传；虚假陈述",
     "The lawsuit was based on misrepresentation of facts.", "这起诉讼是基于对事实的歪曲。"),
    ("anonymity", "/ˌænəˈnɪməti/", "n. 匿名；匿名性",
     "The internet provides a sense of anonymity.", "互联网提供了一种匿名感。"),
    ("individual", "/ˌɪndɪˈvɪdʒuəl/", "n. 个人；个体\nadj. 单独的；个别的；独特的",
     "Each individual has unique strengths.", "每个人都有独特的优势。"),
    ("strip away", "", "phr. 剥去；去掉；揭露",
     "Strip away the marketing and the product is quite basic.", "去掉营销包装，产品其实很基础。"),
    ("commodified", "/kəˈmɑːdɪfaɪd/", "adj. 商品化的（commodify的过去分词）",
     "Education has become increasingly commodified.", "教育已经越来越商品化。"),
    ("implication", "/ˌɪmplɪˈkeɪʃn/", "n. 含意；可能的影响；暗示；牵连",
     "The implications of this decision are enormous.", "这个决定的影响是巨大的。"),
    ("dystopia", "/dɪsˈtoʊpiə/", "n. 反乌托邦；极坏的社会",
     "The novel depicts a dystopia where freedom is forbidden.", "这部小说描绘了一个自由被禁止的反乌托邦世界。"),
    ("scurry", "/ˈskɜːri/", "v. 碎步疾跑；仓皇奔跑\nn. 快步急跑",
     "Mice scurried across the kitchen floor.", "老鼠在厨房地板上急跑。"),
    ("inspects", "/ɪnˈspekts/", "v. 检查；视察；审查（inspect的三单）",
     "The manager inspects the factory every week.", "经理每周检查工厂。"),
    ("squabble", "/ˈskwɑːbl/", "n. 争论；口角\nv. （为小事）争吵",
     "The children were squabbling over a toy.", "孩子们在为一个玩具争吵。"),
    ("dysfunction", "/dɪsˈfʌŋkʃn/", "n. 功能障碍；关系失衡",
     "Family dysfunction can affect children's development.", "家庭功能障碍会影响儿童的发展。"),
    ("logistics", "/ləˈdʒɪstɪks/", "n. 物流；后勤；组织工作",
     "The logistics of the event were handled perfectly.", "活动的后勤工作处理得很完美。"),
    ("capitulation", "/kəˌpɪtʃuˈleɪʃn/", "n. 投降；屈服",
     "The capitulation of the army ended the war.", "军队的投降结束了战争。"),
    ("escalation", "/ˌeskəˈleɪʃn/", "n. 升级；扩大；逐步增加",
     "There are fears of an escalation in the conflict.", "人们担心冲突升级。"),
    ("stalemate", "/ˈsteɪlmeɪt/", "n. 僵局；相持\nv. 使陷入僵局",
     "The negotiations ended in a stalemate.", "谈判以僵局告终。"),
    ("prolong", "/prəˈlɔːŋ/", "v. 延长；拖延",
     "Smoking can prolong the healing process.", "吸烟会延长愈合过程。"),
    ("permanently", "/ˈpɜːrmənəntli/", "adv. 永久地；永远；长期",
     "The accident left him permanently disabled.", "事故使他永久残疾。"),
    ("desperation", "/ˌdespəˈreɪʃn/", "n. 绝望；铤而走险；拼命",
     "In desperation, he called for help.", "在绝望中，他呼救。"),
    ("hostage", "/ˈhɑːstɪdʒ/", "n. 人质",
     "The hostages were held for three days.", "人质被关押了三天。"),
    ("leverage", "/ˈlevərɪdʒ/", "n. 杠杆作用；影响力；筹码\nv. 利用",
     "We can leverage technology to improve education.", "我们可以利用技术来改善教育。"),
    ("starvation", "/stɑːrˈveɪʃn/", "n. 饥饿；饿死；挨饿",
     "Millions of people face starvation in the region.", "该地区数百万人面临饥饿。"),
    ("rig", "/rɪɡ/", "n. 钻机；装备\nv. 操纵；装配",
     "The election was rigged by corrupt officials.", "选举被腐败官员操纵了。"),
    ("craft", "/kræft/", "n. 工艺；手艺；飞行器\nv. 精心制作",
     "She spent hours crafting a beautiful letter.", "她花了几个小时精心制作了一封漂亮的信。"),
    ("ethical", "/ˈeθɪkl/", "adj. 道德的；伦理的；合乎道德的",
     "Is it ethical to test products on animals?", "在动物身上测试产品合乎道德吗？"),
    ("deception", "/dɪˈsepʃn/", "n. 欺骗；骗局；骗术",
     "The scheme was based on deception from the start.", "这个计划从一开始就建立在欺骗之上。"),
    ("poverty", "/ˈpɑːvərti/", "n. 贫困；贫穷；贫乏",
     "Many families live in poverty in this area.", "这个地区许多家庭生活在贫困中。"),
    ("sewn", "/soʊn/", "v. 缝制（sew的过去分词）",
     "The dress was hand-sewn by her grandmother.", "这条裙子是她奶奶手工缝制的。"),
    ("smokescreen", "/ˈsmoʊkskriːn/", "n. 烟幕；障眼法",
     "His apology was just a smokescreen to hide his real intentions.", "他的道歉只是一个烟幕，用来掩盖他真正的意图。"),
    ("continent", "/ˈkɑːntɪnənt/", "n. 大陆；洲",
     "Africa is the second largest continent.", "非洲是第二大大陆。"),
    ("advocate", "/ˈædvəkeɪt/", "v. 提倡；拥护\nn. 拥护者；辩护律师",
     "She advocates for equal rights in education.", "她倡导教育中的平等权利。"),
    ("attorney", "/əˈtɜːrni/", "n. 律师；代理人",
     "You should consult an attorney before signing the contract.", "签合同前你应该咨询律师。"),
    ("bootstrapped", "/ˈbuːtstræpt/", "adj. 自力更生的；自举的",
     "The company was bootstrapped with only $5,000.", "这家公司仅用5000美元自力更生创办。"),
    ("cripple", "/ˈkrɪpl/", "v. 使残废；严重毁坏\nn. 残疾人",
     "The sanctions could cripple the country's economy.", "制裁可能严重损害这个国家的经济。"),
    ("instead of", "", "prep. 代替；而不是",
     "I'll have tea instead of coffee.", "我要茶而不是咖啡。"),
    ("devastating", "/ˈdevəsteɪtɪŋ/", "adj. 毁灭性的；令人难受的；压倒性的",
     "The hurricane had a devastating impact on the coast.", "飓风对海岸造成了毁灭性的影响。"),
    ("pipeline", "/ˈpaɪplaɪn/", "n. 管道；渠道；酝酿中的事物",
     "We have several new products in the pipeline.", "我们有几个新产品正在开发中。"),
    ("opponent", "/əˈpoʊnənt/", "n. 对手；竞争者；反对者",
     "She defeated her opponent in the final round.", "她在最后一轮击败了对手。"),
    ("interaction", "/ˌɪntərˈækʃn/", "n. 互动；相互作用",
     "Social interaction is important for mental health.", "社交互动对心理健康很重要。"),
    ("resume", "/rɪˈzuːm/", "v. 继续；重新开始\nn. 简历",
     "The meeting will resume after a short break.", "会议将在短暂休息后继续。"),
    ("orchestra", "/ˈɔːrkɪstrə/", "n. 管弦乐队；管弦乐团",
     "The orchestra performed Beethoven's Fifth Symphony.", "管弦乐队演奏了贝多芬的第五交响曲。"),
    ("eliminate", "/ɪˈlɪmɪneɪt/", "v. 消除；消灭；淘汰",
     "We need to eliminate unnecessary costs.", "我们需要消除不必要的成本。"),
    ("villain", "/ˈvɪlən/", "n. 恶棍；反面人物；罪魁祸首",
     "Every good story needs a convincing villain.", "每个好故事都需要一个令人信服的反派。"),
    ("fallacy", "/ˈfæləsi/", "n. 谬误；谬论；错误推理",
     "It's a common fallacy that more money equals more happiness.", "更多的钱等于更多的幸福是一个常见的谬误。"),
    ("catastrophically", "/ˌkætəˈstrɑːfɪkli/", "adv. 灾难性地",
     "The project failed catastrophically.", "项目灾难性地失败了。"),
    ("vulnerable", "/ˈvʌlnərəbl/", "adj. 脆弱的；易受攻击的；易受伤害的",
     "Children are particularly vulnerable to online threats.", "儿童尤其容易受到网络威胁。"),
    ("validation", "/ˌvælɪˈdeɪʃn/", "n. 验证；确认；核实",
     "She doesn't need anyone else's validation.", "她不需要任何人的认可。"),
    ("flagship", "/ˈflæɡʃɪp/", "n. 旗舰；旗舰产品；王牌",
     "The new phone is the company's flagship product.", "新手机是公司的旗舰产品。"),
    ("conduct", "/kənˈdʌkt/", "v. 实施；执行；引导；指挥\nn. 举止；行为",
     "The company conducted a survey of customer satisfaction.", "公司进行了一项客户满意度调查。"),
    ("aspect", "/ˈæspekt/", "n. 方面；层面；外观",
     "We need to consider every aspect of the problem.", "我们需要考虑问题的每一个方面。"),
    ("pattern", "/ˈpætərn/", "n. 模式；方式；图案\nv. 构成图案",
     "There is a clear pattern in the data.", "数据中有一个清晰的模式。"),
    ("segment", "/ˈseɡmənt/", "n. 段；部分；片\nv. 分割；划分",
     "The company targets a specific market segment.", "公司针对一个特定的市场细分。"),
]

# 生成词条文本
entries = []
for word, phonetic, meanings, ex_en, ex_cn in NEW_WORDS:
    if word.lower().replace(" ", "_") in {w.lower() for w in EXISTING}:
        continue
    entry = f"""
---

### {word}

**词性和含义**

- **词性**：{meanings.split('；')[0].split('.')[0] + '.' if '.' in meanings.split('；')[0] else ''}
- **音标**：{phonetic if phonetic else 'N/A'}
- **中文释义**：
{chr(10).join('  - ' + line.strip() for line in meanings.split(chr(10)) if line.strip())}

**实际应用场景**

- **例句**：
  - EN: {ex_en}
  - CN: {ex_cn}

- **首次记录**：{TODAY}
- **提问次数**：1
"""
    entries.append(entry)

# 追加到词库
with open(WORDS_FILE, "a", encoding="utf-8") as f:
    for entry in entries:
        f.write(entry)

print(f"已添加 {len(entries)} 个新单词到词库")

# 更新提问日志
log_lines = []
for word, _, _, _, _ in NEW_WORDS:
    if word.lower().replace(" ", "_") in {w.lower() for w in EXISTING}:
        continue
    log_lines.append(f"| {TODAY} | {word} 的含义和用法 | 单词 | 1 | 新学 |")

with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")

print(f"已更新提问日志，新增 {len(log_lines)} 条记录")
