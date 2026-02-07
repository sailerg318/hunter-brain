# app.py
import streamlit as st
import json
import re
from datetime import datetime

# 【优化：页面配置必须在最前面】
st.set_page_config(page_title="NEXUS · TALENT INTELLIGENCE", layout="wide", page_icon="🧠")

# 【优化：懒加载重量级库，只在需要时导入】
_heavy_libs_loaded = False

def lazy_import_heavy_libs():
    """延迟导入重量级库，加快初始加载速度"""
    global pd, requests, io, base64, fitz, Document, _heavy_libs_loaded
    if _heavy_libs_loaded:
        return
    import pandas as pd
    import requests
    import io
    import base64
    import fitz  # PyMuPDF
    from docx import Document
    _heavy_libs_loaded = True

# 【优化1】使用本地缓存的Font Awesome，避免CDN延迟
@st.cache_data
def load_font_awesome():
    return '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">'

st.markdown(load_font_awesome(), unsafe_allow_html=True)

# 【优化2】将CSS提取为缓存函数，避免每次重新解析
# 【性能优化】大幅简化CSS，移除复杂光晕和模糊效果
@st.cache_data
def load_custom_css():
    return """
<style>
/* 简化背景 - 移除复杂光晕效果 */
.stApp {
    background: #0a0b1e !important;
    color: #e0e6ff !important;
}

body {
    background: #0a0b1e !important;
}

/* 侧边栏 - 简化样式（无光影） */
[data-testid="stSidebar"] {
    background: rgba(20, 25, 45, 0.5) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: none !important;
}

/* 侧边栏内所有组件 - 无光影 */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] [data-testid="stSelectbox"],
[data-testid="stSidebar"] [data-baseweb="notification"] {
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: rgba(30, 35, 60, 0.3) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] input:focus,
[data-testid="stSidebar"] textarea:focus {
    border-color: rgba(255, 255, 255, 0.2) !important;
    box-shadow: none !important;
}

/* 侧边栏内的selectbox - 更小尺寸 */
[data-testid="stSidebar"] [data-baseweb="select"] {
    font-size: 0.7rem !important;
    min-height: 28px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    font-size: 0.7rem !important;
    padding: 0.25rem 0.4rem !important;
    min-height: 28px !important;
    line-height: 1.2 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] input {
    font-size: 0.7rem !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg {
    width: 16px !important;
    height: 16px !important;
}

/* 侧边栏内的selectbox选项下拉菜单 */
[data-testid="stSidebar"] [role="listbox"] {
    font-size: 0.7rem !important;
}
[data-testid="stSidebar"] [role="option"] {
    font-size: 0.7rem !important;
    padding: 0.35rem 0.5rem !important;
    min-height: 28px !important;
}

/* 侧边栏内的slider也缩小 */
[data-testid="stSidebar"] [data-testid="stSlider"] {
    font-size: 0.7rem !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div {
    font-size: 0.7rem !important;
}

/* 颜色和字体 */
body, .stMarkdown, .stText {
    color: #e0e6ff !important;
    font-size: 11pt !important;
}

/* 标题 - 柔和渐变 */
h1, h2, h3, h4, h5, h6 {
    background: linear-gradient(135deg, #ff69b4 0%, #ba55d3 50%, #00bfff 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 600 !important;
    text-shadow: none !important;
}

/* 段落文本 */
p, span, label {
    color: #d0d8f0 !important;
}

/* 简化按钮样式 - 移除复杂动画和阴影 */
.stButton > button {
    background: rgba(138, 43, 226, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    padding: 0.6rem 1.2rem !important;
    font-size: 10pt !important;
    transition: background 0.2s ease !important;
}

.stButton > button:hover {
    background: rgba(138, 43, 226, 0.7) !important;
}

/* 简化输入框样式 - 移除复杂渐变和阴影 */
input, textarea, select {
    background: rgba(30, 35, 60, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 6px !important;
    color: #e0e6ff !important;
    padding: 0.5rem !important;
    font-size: 10pt !important;
}

input:focus, textarea:focus {
    border-color: rgba(138, 43, 226, 0.6) !important;
    outline: none !important;
}

/* 简化表格样式 */
.styled-table {
    border-collapse: collapse !important;
    width: 100% !important;
}

.styled-table th {
    background: rgba(138, 43, 226, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    padding: 0.8rem !important;
    color: #e0e6ff !important;
}

.styled-table td {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 0.6rem !important;
    color: #d0d8f0 !important;
    background: rgba(20, 25, 45, 0.4) !important;
}

/* 展开器标题 - 简化样式（无光影） */
.streamlit-expanderHeader {
    padding: 0.6rem 0.8rem !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    background: rgba(30, 35, 60, 0.25) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    position: relative !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    font-size: 0.85rem !important;
    opacity: 0.85 !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(30, 35, 60, 0.35) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

/* 隐藏原生按钮 */
[data-testid="stExpanderToggleButton"], .streamlit-expanderHeader > button {
    display: none !important;
    visibility: hidden !important;
}

/* 展开器内容 */
.streamlit-expanderContent {
    padding: 0.8rem !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-top: none !important;
    background: rgba(20, 25, 45, 0.3) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    box-shadow: none !important;
}

/* 自定义箭头指示 */
.streamlit-expanderHeader::after {
    content: "▶" !important;
    font-size: 12px !important;
    background: linear-gradient(135deg, #ff69b4 0%, #ba55d3 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 600 !important;
    margin-left: auto !important;
    padding-left: 10px !important;
}

/* 展开时改变指示符 */
.streamlit-expanderHeader[aria-expanded="true"]::after {
    content: "▼" !important;
    background: linear-gradient(135deg, #00bfff 0%, #ba55d3 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

/* 备注区域 */
.notes-recall {
    font-size: 10pt;
    line-height: 1.8;
    color: #d0d8f0;
    background: rgba(30, 35, 60, 0.3) !important;
    backdrop-filter: blur(15px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(15px) saturate(180%) !important;
    padding: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-left: 3px solid rgba(255, 105, 180, 0.6);
    border-radius: 12px;
    box-shadow: 0 8px 32px 0 rgba(138, 43, 226, 0.2) !important;
    font-family: 'Courier New', monospace;
}

/* 容器边框 */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 12px !important;
    background: rgba(30, 35, 60, 0.3) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    box-shadow: 0 8px 32px 0 rgba(138, 43, 226, 0.2) !important;
}

/* Selectbox和下拉框 */
[data-testid="stSelectbox"] {
    border-radius: 6px !important;
}

/* 简化滚动条 */
::-webkit-scrollbar {
    width: 8px !important;
}

::-webkit-scrollbar-track {
    background: rgba(20, 25, 45, 0.5) !important;
}

::-webkit-scrollbar-thumb {
    background: rgba(138, 43, 226, 0.6) !important;
    border-radius: 4px !important;
}
</style>
"""

st.markdown(load_custom_css(), unsafe_allow_html=True)

# 【优化：常量定义】
API_BASE = "https://api.gemai.cc/v1"
MODEL_NAME = "[官逆]gemini-3-pro-preview"
DEFAULT_KEY = "sk-5gdJnwOpb24drogckyzMQg4mId442uXTl0V8JNYcQdHm1FZH"

# 【优化：Session State 初始化 - 使用 setdefault 更高效】
st.session_state.setdefault('user', None)
st.session_state.setdefault('talents', [])
st.session_state.setdefault('last_result', None)

# =========================
# 全局配置常量（优化3：使用缓存加载配置）
# =========================

@st.cache_data
def get_regions_config():
    return {
    'APAC': {
        'countries': ['日本', '韩国', '新加坡', '印度', '泰国', '越南', '菲律宾', '马来西亚', '印尼', '印度尼西亚', '巴基斯坦', '孟加拉', '台湾', '香港', '澳门', '缅甸', '柬埔寨', '老挝'],
        'keywords': ['亚太', 'apac', '东南亚', '亚洲']
    },
    'EMEA': {
        'countries': ['英国', '法国', '德国', '意大利', '西班牙', '瑞典', '芬兰', '丹麦', '荷兰', '比利时', '瑞士', '奥地利', '捷克', '波兰', '俄罗斯', '葡萄牙', '挪威', '希腊', '匈牙利', '罗马尼亚', '乌克兰', '卢森堡', '爱尔兰', '立陶宛', '拉脱维亚', '爱沙尼亚', '斯洛文尼亚', '斯洛伐克', '克罗地亚', '保加利亚', '塞尔维亚', '波黑', '黑山', '马其顿', '阿尔巴尼亚', '土耳其', '沙特', '阿联酋', '以色列', '伊朗', '伊拉克', '约旦', '黎巴嫩', '卡塔尔', '巴林', '阿曼', '也门', '科威特', '埃及', '南非', '尼日利亚', '肯尼亚', '摩洛哥', '突尼斯', '安哥拉', '喀麦隆', '加纳', '坦桑尼亚', '乌干达', '埃塞俄比亚', '刚果', '几内亚', '塞内加尔', '马里', '布基纳法索', '象牙海岸', '利比亚', '苏丹', '卢旺达', '津巴布韦', '赞比亚', '莫桑比克', '马达加斯加', '毛里求斯'],
        'keywords': ['欧洲', 'emea', '中东', '非洲', '欧中东非']
    },
    'AMS': {
        'countries': ['美国', '加拿大', '墨西哥', '危地马拉', '洪都拉斯', '萨尔瓦多', '尼加拉瓜', '哥斯达黎加', '巴拿马', '伯利兹', '哥伦比亚', '委内瑞拉', '圭亚那', '苏里南', '厄瓜多尔', '秘鲁', '巴西', '玻利维亚', '智利', '阿根廷', '乌拉圭', '巴拉圭'],
        'keywords': ['美洲', 'ams', '北美', '南美', '中美', '拉丁美洲', '加勒比']
    }
    }

@st.cache_data
def get_cities_cn():
    return ['北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '西安', '南京', '苏州', '天津', '重庆', '长沙', '青岛', '宁波', '郑州', '哈尔滨', '沈阳', '大连', '厦门', '福州', '济南', '合肥', '南昌', '石家庄', '太原', '兰州', '昆明', '南宁', '海口', '贵阳', '乌鲁木齐', '呼和浩特', '银川', '西宁', '拉萨', '南通', '无锡', '常州', '镇江', '扬州', '嘉兴', '温州', '绍兴', '台州', '衢州', '金华', '丽水']

# 985、211、QS100学校映射（用于学校标签提取）
@st.cache_data
def get_schools_985():
    return {
    '北京大学', '清华大学', '浙江大学', '复旦大学', '上海交通大学', '中国人民大学', '南京大学', '武汉大学', '中山大学', '四川大学', '吉林大学', '哈尔滨工业大学', '西安交通大学', '南开大学', '天津大学', '同济大学', '厦门大学', '中南大学', '北京师范大学', '华中科技大学', '西北工业大学', '兰州大学', '大连理工大学', '华东师范大学', '中国科学技术大学', '东南大学', '北京航空航天大学', '北京理工大学', '重庆大学', '电子科技大学', '山东大学', '中国农业大学', '华中农业大学', '西南大学', '东北大学', '中央民族大学', '西安电子科技大学', '华南理工大学', '北京工业大学', '郑学', 'Tsinghua', 'Peking', 'Zhejiang', 'Fudan', 'SJTU', 'Renmin'
    }

@st.cache_data
def get_schools_211():
    return {
    # 包含所有985高校，以及其他211高校
    '北京大学', '清华大学', '浙江大学', '复旦大学', '上海交通大学', '中国人民大学', '南京大学', '武汉大学', '中山大学', '四川大学', '吉林大学', '哈尔滨工业大学', '西安交通大学', '南开大学', '天津大学', '同济大学', '厦门大学', '中南大学', '北京师范大学', '华中科技大学', '西北工业大学', '兰州大学', '大连理工大学', '华东师范大学', '中国科学技术大学', '东南大学', '北京航空航天大学', '北京理工大学', '重庆大学', '电子科技大学', '山东大学', '中国农业大学', '华中农业大学', '西南大学', '东北大学', '中央民族大学', '西安电子科技大学', '华南理工大学',
    # 其他211高校
    '北京交通大学', '北京工业大学', '北京科技大学', '北京化工大学', '北京邮电大学', '北京林业大学', '北京中医药大学', '中国传媒大学', '对外经济贸易大学', '中央财经大学', '中国政法大学', '华北电力大学', '中国地质大学', '中国矿业大学', '中国石油大学', '常州大学', '南京航空航天大学', '南京理工大学', '南京邮电大学', '河海大学', '江南大学', '南京农业大学', '南京林业大学', '苏州大学', '南通大学', '扬州大学', '浙江工业大学', '杭州电子科技大学', '浙江理工大学', '浙江农林大学', '安徽大学', '合肥工业大学', '厦门大学', '福州大学', '南昌大学', '华东交通大学', '景德镇陶瓷大学', '江西财经大学', '山东大学', '中国海洋大学', '山东科技大学', '青岛科技大学', '济南大学', '青岛大学', '郑州大学', '河南大学', '河南工业大学', '河南农业大学', '华中师范大学', '华中农业大学', '中南财经政法大学', '武汉理工大学', '武汉工程大学', '湖南大学', '中南大学', '湖南师范大学', '湖南农业大学', '长沙理工大学', '广西大学', '广西师范大学', '广东工业大学', '广州大学', '华南农业大学', '广东外语外贸大学', '汕头大学', '海南大学', '四川大学', '西南交通大学', '西南石油大学', '成都理工大学', '西南民族大学', '贵州大学', '云南大学', '西北大学', '西北工业大学', '西安建筑科技大学', '西安理工大学', '西安电子科技大学', '西安工业大学', '陕西科技大学', '长安大学', '陕西师范大学', '陕西中医药大学', '新疆大学', '石河子大学', '宁夏大学', '青海大学', '内蒙古大学'
    }

@st.cache_data
def get_schools_qs100():
    return {
    # 全球QS前100且与中国相关的高校（含港澳台）
    '清华大学', '北京大学', '香港大学', '香港科技大学', '香港中文大学', '新加坡国立大学', '南洋理工大学', '复旦大学', '上海交通大学', '浙江大学', '中国科学技术大学', '南京大学', '武汉大学', '中山大学', '东京大学', '京都大学', '大阪大学', '东京工业大学', 'Tsinghua', 'Peking', 'HKU', 'HKUST', 'NUS', 'NTU', 'Fudan', 'SJTU', 'Zhejiang', 'USTC'
    }

# 兼容性：保持原有的全局变量名（延迟加载）
REGIONS_CONFIG = None
CITIES_CN = None
SCHOOLS_985 = None
SCHOOLS_211 = None
SCHOOLS_QS100 = None

def _init_globals():
    global REGIONS_CONFIG, CITIES_CN, SCHOOLS_985, SCHOOLS_211, SCHOOLS_QS100
    if REGIONS_CONFIG is None:
        REGIONS_CONFIG = get_regions_config()
        CITIES_CN = get_cities_cn()
        SCHOOLS_985 = get_schools_985()
        SCHOOLS_211 = get_schools_211()
        SCHOOLS_QS100 = get_schools_qs100()

FIELD_MAPPING = {'cn_date': 'comm_date', 'company': 'company_path', 'edu': 'school_tag', 'on_going': 'current_opportunity', 'motivation_summary': 'career_summary'}
PERSONAL_INFO_MAPPING = {'salary': 'salary', 'loc': 'location', 'target_loc': 'pref_location', 'level': 'rank', 'title': 'title', 'phone': 'phone', 'management': 'management', 'family': 'family', 'native': 'native'}

# =========================
# 工具函数
# =========================

def parse_file(file) -> str:
    """解析上传的文件（PDF/DOCX/TXT）"""
    # 懒加载重量级库
    lazy_import_heavy_libs()
    if not file: return ""
    suffix = file.name.lower().split(".")[-1]
    fb = file.read()
    try:
        if suffix == "pdf":
            return " ".join([page.get_text() for page in fitz.open(stream=fb, filetype="pdf")])
        elif suffix in ("docx", "doc"):
            return " ".join([p.text for p in Document(io.BytesIO(fb)).paragraphs])
        else:
            return fb.decode("utf-8", errors="ignore")
    except:
        return fb.decode("utf-8", errors="ignore")

def extract_phone(text):
    """从文本中提取电话号码"""
    if not text: return "未留"
    # 优先匹配11位手机号
    match = re.search(r'1[3-9]\d{9}', text)
    if match: return match.group(0)
    # 匹配座机格式：(010)1234567 或 010-1234567 或 010 1234567或 3位-4位-4位
    patterns = [
        r'\(?0\d{2,3}\)[\s-]?\d{3,4}[\s-]?\d{4}', # (010)1234567, (0571) 1234567
        r'0\d{2,3}\s?\d{3,4}\s?\d{4}',           # 010 1234567
        r'\d{3,4}[-]\d{3,4}[-]\d{4}'               # 010-1234-5678
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match: return match.group(0)
    return "未留"

def extract_city(text, cities_list=None):
    """从文本中提取城市（用于loc、target_loc、native）"""
    if not text: return "未知"
    if cities_list is None:
        cities_list = get_cities_cn()
    for city in cities_list:
        if city in text: return city
    return "未知"

def extract_edu(text):
    """从文本中提取学校标签（985/211/海外或学校名称）
    优先级：985 > 211 > QS100 > 原始学校名称
    """
    if not text: return "未知"
    text_lower = text.lower()
    
    schools_985 = get_schools_985()
    schools_211 = get_schools_211()
    schools_qs100 = get_schools_qs100()
    
    # 1. 检查985
    for school in schools_985:
        if school.lower() in text_lower:
            return "985"
    # 2. 检查211（排除已识别的985）
    for school in schools_211:
        if school.lower() in text_lower and school not in schools_985:
            return "211"
    # 3. 检查QS100（排除已识别的985和211）
    for school in schools_qs100:
        if school.lower() in text_lower and school not in schools_985 and school not in schools_211:
            return "海外"
    
    # 4. 尝试提取实际的大学名称
    # 匹配常见的大学名称模式
    import re
    patterns = [
        r'[\u4e00-\u9fa5]{2,20}(?:大学|学院|理工大学|工业大学|科技大学|师范大学|医科大学|农业大学|财经大学|政法大学|外国语大学|体育大学|艺术学院|音乐学院|美术学院)',
        r'[\u4e00-\u9fa5]{2,20}(?:University|College|Institute)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            school_name = match.group(0)
            # 过滤掉一些无效匹配
            if len(school_name) >= 4 and school_name not in ['大学', '学院', '理工大学']:
                return school_name
                
    # 5. 如果都没匹配到，返回未知
    return "未知"

def extract_intl(notes, cv_text):
    """从文本中提取国际化大区信息（使用全局REGIONS_CONFIG常量）
    - 涉及3个大区 → Global
    - 涉及2个大区 → 按APAC+AMS+EMEA顺序组合
    - 涉及1个大区 → 该大区名称
    - 0个大区 → 无
    """
    combined_text = (notes + cv_text).lower()
    detected_regions = set()
    regions_config = get_regions_config()
    # 遍历各大区检测
    for region, data in regions_config.items():
        # 检查国家关键词
        for country in data['countries']:
            if country.lower() in combined_text:
                detected_regions.add(region)
                break # 不再继续，已经检测到该大区则继续到下一个大区
        if region not in detected_regions:
            # 检查地区关键词
            for keyword in data['keywords']:
                if keyword.lower() in combined_text:
                    detected_regions.add(region)
                    break
    # 根据检测到的大区数量确定输出
    if len(detected_regions) == 0:
        return '无'
    elif len(detected_regions) == 3:
        return 'Global'
    elif len(detected_regions) == 2:
        # 按APAC、AMS、EMEA的优先级排序
        regions_order = ['APAC', 'AMS', 'EMEA']
        sorted_regions = sorted(list(detected_regions), key=lambda x: regions_order.index(x))
        return '+'.join(sorted_regions)
    else:
        return list(detected_regions)[0]

def call_ai_engine(api_key, prompt, model=None, temperature=0.1):
    """
    统一 AI 调用接口 - 支持通用API的所有模型
    Args:
        api_key: API密钥
        prompt: 提示词
        model: 模型名称（默认用 MODEL_NAME）
        temperature: 温度参数（0-1，越低越确定）
    """
    if model is None:
        model = MODEL_NAME
        
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system", 
                "content": "You are a SAILER V3.3 headhunting system. Strictly follow SAILER V3.3 protocol and output JSON matching the requested schema."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"}
    }
    
    try:
        r = requests.post(f"{API_BASE}/chat/completions", headers=headers, json=payload, timeout=120)
        # 检查响应状态码
        if r.status_code != 200:
            error_msg = f"API 返回错误 ({r.status_code}): {r.text[:500]}"
            st.error(error_msg)
            return None
            
        resp_json = r.json()
        
        # 检查是否有错误信息
        if "error" in resp_json:
            error_msg = f"API 错误: {resp_json['error'].get('message', str(resp_json['error']))}"
            st.error(error_msg)
            return None
            
        # 检查是否有 choices 字段
        if "choices" not in resp_json:
            error_msg = f"API 响应格式错误：缺少 'choices' 字段。响应内容: {str(resp_json)[:300]}"
            st.error(error_msg)
            return None
            
        if len(resp_json["choices"]) == 0:
            st.error("API 返回空结果")
            return None
            
        # 提取内容
        c = resp_json["choices"][0]["message"]["content"]
        start, end = c.find('{'), c.rfind('}')
        if start == -1:
            st.error(f"响应内容中找不到 JSON 对象: {c[:200]}")
            return None
        return json.loads(re.sub(r'//.*?\n', ' ', c[start:end+1]))
    except requests.exceptions.Timeout:
        st.error(f"⏱ 请求超时 (120s)：{model} 响应过慢，请重试或选择更快的模型")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🌐 网络错误: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON 解析失败: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ 未知错误: {str(e)}")
        return None

def get_value(res: dict, keys, default="—"):
    if not res: return default
    if isinstance(keys, str): keys = [keys]
    
    # 逻辑 1: 路径深度扫描 (针对 nested personal_info)
    for k in keys:
        if "." in k:
            parts = k.split(".")
            temp = res
            for p in parts:
                if isinstance(temp, dict) and p in temp:
                    temp = temp[p]
                else:
                    temp = None
                    break
            if temp not in (None, "", [], {}):
                return str(temp) if not isinstance(temp, list) else ", ".join([str(x) for x in temp])
                
    # 逻辑 2: 全字典展平 + 键名归一化 (匹配中文和无标点键名)
    lookup = {}
    def _norm(s): return re.sub(r'[^\w\u4e00-\u9fff]', '', str(s).lower())
    def flatten(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                lookup[_norm(k)] = v
                if isinstance(v, dict): flatten(v)
    flatten(res)
    for k in keys:
        nk = _norm(k)
        if nk in lookup:
            v = lookup[nk]
            if v not in (None, "", [], {}):
                return ", ".join([str(x) for x in v]) if isinstance(v, list) else str(v)
    return default

def render_profile(res: dict):
    if not res: return
    name = get_value(res, ['name', '姓名'])
    summary = get_value(res, ['summary', '摘要', 'executive_summary'])
    
    st.markdown(f"""
        <h3 style="font-size: 1.3rem; margin-bottom: 0.5rem;">
            <i class="fas fa-user-circle" style="margin-right: 0.5rem; opacity: 0.8; background: linear-gradient(135deg, #ff69b4 0%, #ba55d3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
            <span style="background: linear-gradient(135deg, #ff69b4 0%, #ba55d3 50%, #00bfff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{name}</span>
        </h3>""", unsafe_allow_html=True)
    
    st.markdown(f'<p style="font-size: 0.85rem; line-height: 1.6; opacity: 0.9;"><strong>摘要</strong>: {summary}</p>', unsafe_allow_html=True)
    
    if res.get("raw_notes"):
        with st.expander("📝 原始沟通记录", expanded=True):
            st.markdown(f'<div class="notes-recall">{res["raw_notes"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<h4 style="font-size: 0.95rem; margin-bottom: 0.8rem;">
                <i class="fas fa-brain" style="margin-right: 0.4rem; opacity: 0.8; background: linear-gradient(135deg, #ff69b4 0%, #ba55d3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
                <span style="background: linear-gradient(135deg, #ff69b4 0%, #ba55d3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">主观画像</span>
            </h4>""", unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>沟通日期</strong>: {get_value(res, ["comm_date", "沟通日期"])}</p>', unsafe_allow_html=True)
            motive_tag = get_value(res, ['career_motive', '职业动因', '动因'])
            motive_summary = get_value(res, ['motivation_summary', '职业动因总结', 'career_summary'], "")
            motive_display = f"{motive_tag}" + (f" - {motive_summary}" if motive_summary not in ("", "—") else "")
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>职业动因</strong>: {motive_display}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>稳定性</strong>: {get_value(res, ["stability_tag", "稳定性评级", "稳定性"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>看机会</strong>: {get_value(res, ["tags.opportunity_attitude", "opportunity_attitude", "看机会"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>经验标签</strong>: {get_value(res, ["experience_tags", "经验标签", "经验"])}</p>', unsafe_allow_html=True)
        with c2:
            st.markdown("""<h4 style="font-size: 0.95rem; margin-bottom: 0.8rem;">
                <i class="fas fa-chart-line" style="margin-right: 0.4rem; opacity: 0.8; background: linear-gradient(135deg, #ba55d3 0%, #00bfff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
                <span style="background: linear-gradient(135deg, #ba55d3 0%, #00bfff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">客观标签</span>
            </h4>""", unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>学校</strong>: {get_value(res, ["school_tag", "学校背景", "学校"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>年龄</strong>: {get_value(res, ["age_tag", "年龄"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>公司历程</strong>: {get_value(res, ["company_path", "公司历程", "公司"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>国际化</strong>: {get_value(res, ["global_region", "国际化经验", "国际化"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>管理规模</strong>: {get_value(res, ["personal_info.management", "management", "管理规模", "管理"])}</p>', unsafe_allow_html=True)
        with c3:
            st.markdown("""<h4 style="font-size: 0.95rem; margin-bottom: 0.8rem;">
                <i class="fas fa-id-card" style="margin-right: 0.4rem; opacity: 0.8; background: linear-gradient(135deg, #00bfff 0%, #ba55d3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
                <span style="background: linear-gradient(135deg, #00bfff 0%, #ba55d3 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">个人信息</span>
            </h4>""", unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>目前在聊</strong>: <span style="color: #ff4444;">{get_value(res, ["current_opportunity", "目前在聊机会", "在聊机会"])}</span></p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>薪资</strong>: {get_value(res, ["personal_info.salary", "salary", "薪资"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>目前/倾向</strong>: {get_value(res, ["personal_info.location", "location", "所在地"])} → {get_value(res, ["personal_info.pref_location", "pref_location", "倾向地点"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>职级</strong>: {get_value(res, ["personal_info.rank", "rank", "职级"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>家庭</strong>: {get_value(res, ["personal_info.family", "family", "家庭情况"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>籍贯</strong>: {get_value(res, ["personal_info.native", "native", "籍贯"])}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 0.8rem; line-height: 1.8; margin-bottom: 0.3rem;"><strong>电话</strong>: {get_value(res, ["personal_info.phone", "phone", "电话"])}</p>', unsafe_allow_html=True)
            
    if res.get("raw_cv_text"):
        with st.expander("简历原文"):
            st.markdown(f'<div class="notes-recall">{res["raw_cv_text"]}</div>', unsafe_allow_html=True)
    with st.expander("原始数据"):
        st.json(res)

# =========================
# APP 逻辑
# =========================

if not st.session_state['user']:
    # 【优化：简化登录页面，减少渲染时间】
    st.title("🧠 NEXUS · TALENT INTELLIGENCE")
    st.caption("AI-Driven Talent Intelligence Platform · Powered by SAILER V3.3")
    st.divider()
    
    u = st.text_input("用户名")
    s = st.file_uploader("导入快照", type=["json"])
    if st.button("进入系统", use_container_width=True):
        if u: 
            st.session_state['user'] = u
            if s: st.session_state['talents'] = json.load(s)
            st.rerun()
    st.stop()

# 侧边栏菜单 - 使用Font Awesome图标
st.sidebar.markdown("### <i class='fas fa-bars icon-primary'></i> 功能模块", unsafe_allow_html=True)
menu = st.sidebar.radio("", ["◆ 单个打标", "◆ 资产看板"], label_visibility="collapsed")

api_key = st.sidebar.text_input("◆ API Key", value="", type="password", help="粘贴您的 API Key（支持 Ctrl+V 或 Cmd+V）")

# 【新增】模型选择面板
with st.sidebar.expander("AI 模型配置"):
    st.markdown('<p style="font-size: 0.75rem; font-weight: 500; opacity: 0.7; margin-bottom: 0.4rem;">选择模型</p>', unsafe_allow_html=True)
    model_presets = {
        "Gemini Flash A": "[满血A]gemini-3-flash-preview",
        "Qwen Max": "[官逆]qwen3-max-2025-10-20",
        "Gemini Pro (推荐)": "[官逆]gemini-3-pro-preview",
        "Gemini Pro Thinking": "[官逆C]gemini-3-pro-preview-thinking",
        "Gemini Pro Max D": "[满血D]gemini-2.5-pro-maxthinking",
        "Gemini Flash Thinking": "[满血C]gemini-2.5-flash-thinking",
        "DeepSeek v3.2 Thinking": "deepseek-v3.2-thinking",
        "DeepSeek v3.2": "deepseek-v3.2",
        "MiniMax M2": "minimax-m2",
        "Grok 4.1 Thinking": "grok-4.1-thinking",
        "Grok 4": "grok-4",
    }
    
    selected_preset = st.selectbox("预设配置", list(model_presets.keys()), label_visibility="collapsed")
    selected_model = model_presets[selected_preset]
    
    # 显示模型详情
    model_info = {
        "[满血A]gemini-3-flash-preview": "速度: 快 | 精度: 高 | 轻量快速",
        "[官逆]qwen3-max-2025-10-20": "速度: 快 | 精度: 高 | 平衡优秀",
        "[官逆]gemini-3-pro-preview": "速度: 中 | 精度: 极高 | 综合最强",
        "[官逆C]gemini-3-pro-preview-thinking": "速度: 中 | 精度: 极高 | 深度推理",
        "[满血D]gemini-2.5-pro-maxthinking": "速度: 慢 | 精度: 极高 | 极限精度",
        "[满血C]gemini-2.5-flash-thinking": "速度: 中 | 精度: 高 | 速度均衡",
        "deepseek-v3.2-thinking": "速度: 慢 | 精度: 极高 | 国产顶级",
        "deepseek-v3.2": "速度: 中 | 精度: 高 | 均衡稳定",
        "minimax-m2": "速度: 快 | 精度: 高 | 快速处理",
        "grok-4.1-thinking": "速度: 中 | 精度: 极高 | 推理能力强",
        "grok-4": "速度: 中 | 精度: 极高 | 综合能力强",
    }
    st.markdown(f'<p style="font-size: 0.65rem; opacity: 0.6; line-height: 1.3; margin-top: 0.3rem;">{model_info.get(selected_model, "N/A")}</p>', unsafe_allow_html=True)
    
    # 温度调节（影响精度和创意度）
    st.markdown('<p style="font-size: 0.8rem; font-weight: 500; opacity: 0.8; margin-top: 1rem; margin-bottom: 0.5rem;">🌡️ 温度参数</p>', unsafe_allow_html=True)
    temperature = st.slider(
        "确定性 ← → 创意性", 
        min_value=0.0, max_value=1.0, value=0.1, step=0.05,
        help="0.1: 最确定（推荐） | 0.5: 平衡 | 1.0: 最创意",
        key="temp_slider",
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown('<p style="font-size: 0.8rem; font-weight: 500; opacity: 0.8; margin-bottom: 0.5rem;">📋 推荐配置方案</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="font-size: 0.7rem; line-height: 1.5; opacity: 0.75;">
        <strong>⚡ 快速方案</strong><br>
        模型：Gemini Flash<br>
        耗时：0.8s<br>
        用途：简单字段
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="font-size: 0.7rem; line-height: 1.5; opacity: 0.75;">
        <strong>⭐ 平衡方案</strong><br>
        模型：Gemini Pro<br>
        耗时：1.0-1.2s<br>
        精度：⭐⭐⭐⭐⭐
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="font-size: 0.7rem; line-height: 1.5; opacity: 0.75;">
        <strong>💎 精度方案</strong><br>
        模型：DeepSeek v3.2<br>
        耗时：1.5-2.0s<br>
        思维链推理
        </div>
        """, unsafe_allow_html=True)

if menu == "◆ 单个打标":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                <i class='fas fa-bullseye' style='margin-right: 0.5rem; opacity: 0.8;'></i> TALENT PROFILER
            </h2>
            <p style="font-size: 0.9rem; opacity: 0.6; letter-spacing: 0.1em;">
                AI-POWERED DEEP TAGGING · 智能深度打标
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    cl, cr = st.columns(2)
    with cl: cv_f = st.file_uploader("上传简历")
    with cr: nt_f = st.text_area("沟通记录")
    
    if st.button("开始 AI 打标", use_container_width=True) and (cv_f or nt_f):
        with st.spinner("正在执行 V3.3 深度分析..."):
            cv_txt = parse_file(cv_f)
            prompt = f"""
            你是一个猎头专家，严格执行 SAILER V3.3 协议。
            当前日期：{datetime.now().strftime('%Y/%m/%d')}。

            【核心权重规则】
            - 摘要: CV(0.5) vs Notes(0.5)。综合分析候选人的核心价值与关键信息，100字内。
            - 主观标签 (职业动因/稳定性): Notes(0.8) vs CV(0.2)。若冲突，以 Notes 为准。
            - 客观标签 (学历/年龄/公司): CV(0.6) vs Notes(0.4)。
            - 个人信息 (薪资/在聊机会): Notes(1.0) 唯一。

            【任务】分析以下内容并打标。
            Notes: {nt_f}
            CV: {cv_txt}

            【定义规范 & 强制要求】
            - name: 候选人姓名，必填
            - company: 公司历程，格式为简称+简称，如"华为+腾讯"，必填
            - title: 最近职位名称，必填
            - level: 职级，从Notes里分析，通常为字母+数字，如P8、L9、T4、Ban6，或数字+"-"+数字，如1-2，必填（若无写未公开）
            - salary: 年薪，格式如"80W"或"100-150W"，必填（若无则写"未公开"）
            - edu: 【注】本字段由后端代码从原始文本中精准提取（985/211/海外分类或大学名称），无需AI处理。若AI回复可以任意填充
            - age_tag: 首先分析CV中出生年月，用当前日期减去出生年月得出准确年龄，若简历无则根据读大学的时间得出形如"约35岁"的年龄估算【必填】
            - management: 【必填】管理规模，根据Notes分析得出如"10人"或"50-100人"或"无直接管理"
            - family: 【必填】家庭状态，如"已婚有俩娃"或"单身"或"未知"
            - native: 【必填】籍贯，如"北京"或"湖南"或"未知"
            - on_going: 【必填】当前在聊机会。必须提取 Notes 中"面试、Offer、在聊"字眼，格式：公司-岗位，若无则写"无"
            - loc: 当前工作地，必填
            - target_loc: 倾向工作地，必填
            - tags.motivation: 【严格枚举】只能从以下选一个：技术精进、管理晋升、自主独立、生活平衡、纯粹挑战
            - tags.stability: 【严格枚举】只能从以下选一个：非常稳定(5年内无跳槽)、稳定(五年内2次)、不稳定(五年内3次+，或近段不足1年)
            - motivation_summary: 【新增必填】用 1-2 句话总结职业动因背后的具体原因和期望，如"渴望在更大平台做技术管理，带领团队"或"想从技术转向管理"（15字内）
            - opportunity_attitude: 【新增必填，根据Notes分析】看机会的态度，【严格枚举】只能从以下选一个：迫切看（主动表达强烈兴趣、频繁询问进展）、主动看（积极参与、认可机会）、被动看（被动接触、可考虑但不主动）、完全不看（明确表示不感兴趣或已决定）
            - summary: 【必填】摘要，权重 CV(0.5) vs Notes(0.5)。综合分析候选人的核心竞争力、关键经历和职业目标，100字内。
            - experience_tags: 【新增必填】关键经验体系标签。(1) 从Notes中识别该候选人最相关的经验类型，严格从以下枚举选择：变革经验、0-1经验、顶层设计经验、执行经验；(2) 根据CV和Notes综合判断，选出最相关的2个标签，用逗号分隔。格式："标签1,标签2"（如："变革经验,团队管理"或"0-1经验,技术架构"或"顶层设计,执行力"）。

            【注】phone、edu、tags.intl 由后端代码从原始文本中精准提取，无需AI处理。

            请严格输出以下 JSON（仅 JSON），所有字段必填，不能为空字符串：
            {{
              "cn_date": "YYYY/MM/DD",
              "name": "姓名",
              "company": "历程",
              "title": "职位",
              "level": "职级",
              "salary": "薪资",
              "edu": "985/211/海外/大学名称",
              "age_tag": "约XX岁",
              "management": "管理规模或无",
              "family": "家庭状态",
              "native": "籍贯",
              "on_going": "公司-岗位或无",
              "loc": "当前城市",
              "target_loc": "倾向城市",
              "summary": "摘要（100字内）",
              "experience_tags": "标签1,标签2",
              "tags": {{"motivation": "动因标签", "stability": "稳定性"}},
              "motivation_summary": "职业动因详细分析（15字内）",
              "opportunity_attitude": "看机会状态",
              "conflict_report": "权重处理说明"
            }}
            严格只返回符合结构的 JSON，所有字段必须有值，不能为空。
            """
            res = call_ai_engine(api_key, prompt, model=selected_model, temperature=temperature)
            if res:
                # 保存原始文本
                res["raw_notes"], res["raw_cv_text"] = nt_f, cv_txt
                
                # 预处理提取（代码提取，比AI更精准）
                combined_text = nt_f + cv_txt
                res['phone'] = extract_phone(combined_text)
                res['edu'] = extract_edu(combined_text)
                res['tags']['intl'] = extract_intl(nt_f, cv_txt)
                
                # 简化字段映射（顶级字段）
                for old_key, new_key in FIELD_MAPPING.items():
                    if old_key in res and not res.get(new_key):
                        res[new_key] = res[old_key]
                
                # tags 字段展开
                tags = res.get('tags') or {}
                if tags:
                    if not res.get('career_motive') and tags.get('motivation'):
                        res['career_motive'] = tags.get('motivation')
                    if not res.get('stability_tag') and tags.get('stability'):
                        res['stability_tag'] = tags.get('stability')
                
                if 'tags' not in res: res['tags'] = {}
                if 'intl' not in res['tags']: res['tags']['intl'] = extract_intl(nt_f, cv_txt)

                # 映射global_region用于render_profile显示
                if not res.get('global_region') and res.get('tags', {}).get('intl'):
                    res['global_region'] = res['tags']['intl']

                # personal_info 聚合（简化版）
                pi = res.get('personal_info') or {}
                for ai_key, pi_key in PERSONAL_INFO_MAPPING.items():
                    if ai_key in res and not pi.get(pi_key):
                        pi[pi_key] = res[ai_key]
                if pi: res['personal_info'] = pi
                
                # 顶级字段补充
                if 'age_tag' in res and not res.get('age'):
                    res['age'] = res.get('age_tag')

                st.session_state['last_result'] = res
                st.rerun()

    if st.session_state['last_result']:
        render_profile(st.session_state['last_result'])
        if st.button("✓ 确认入库", use_container_width=True):
            st.session_state['talents'].append(st.session_state['last_result'])
            st.session_state['last_result'] = None
            st.success("资产已固化")

elif menu == "◆ 资产看板":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                <i class='fas fa-database' style='margin-right: 0.5rem; opacity: 0.8;'></i> TALENT POOL
            </h2>
            <p style="font-size: 0.9rem; opacity: 0.6; letter-spacing: 0.1em;">
                ASSET DASHBOARD · 人才资产看板
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state['talents']:
        t_data = []
        for idx, t in enumerate(st.session_state['talents']):
            pi = t.get("personal_info") or t
            t_data.append({
                "ID": idx,
                "沟通日期": get_value(t, ["comm_date", "沟通日期"]),
                "任职公司": get_value(t, ["company_path", "公司历程", "公司"]),
                "姓名": get_value(t, ["name", "姓名"]),
                "职位": get_value(t, ["personal_info.rank", "rank", "职位", "职级"]),
                "职级": get_value(t, ["personal_info.rank", "rank", "职级"]),
                "年薪": get_value(pi, ["salary", "薪资"]),
                "学历": get_value(t, ["school_tag", "学校"]),
                "在聊机会": get_value(t, ["current_opportunity", "目前在聊机会", "在聊机会"]),
                "目前工作地": get_value(pi, ["location", "所在地"]),
                "可跨越城市": get_value(pi, ["pref_location", "倾向地点"]),
                "电话": get_value(pi, ["phone", "电话"])
            })
        df = pd.DataFrame(t_data)
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True, hide_index=True)
        
        st.divider()
        c1, c2 = st.columns([3, 1])
        with c1:
            target_name = st.selectbox("选择人选回溯详情", df["姓名"].tolist())
        with c2:
            # 找到对应 ID 进行删除
            target_idx = df[df["姓名"] == target_name]["ID"].values[0]
            if st.button("✕ 删除选定人选", use_container_width=True):
                st.session_state['talents'].pop(int(target_idx))
                st.success(f"已移除 {target_name}")
                st.rerun()
                
        selected = next((t for t in st.session_state['talents'] if get_value(t, ["name", "姓名"]) == target_name), None)
        if selected:
            render_profile(selected)
            
        st.download_button("⬇ 导出快照", data=json.dumps(st.session_state['talents'], ensure_ascii=False), file_name="Pool.json")
    else:
        st.info("库内暂无人选")
