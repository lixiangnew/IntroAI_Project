<template>
    <div class="container">
        <h2>山水画生成模型</h2>

        <div class="input-bar">
            <textarea v-model="inputText" placeholder="请输入描述..." @input="autoResize"
                @keydown.enter.prevent="handleEnter" ref="textarea"></textarea>
            <button class="send-button" @click="generate">↑</button>
        </div>


        <div v-for="(item, index) in items" :key="index" class="item">
            <!-- 用户文字 -->
            <div class="user-text-wrapper">
                <div v-if="item.text" class="user-text">
                    {{ item.text }}
                </div>
            </div>
            <!-- loading -->
            <div v-if="item.loading" class="loading-container">
                <h3 class="loading-text">正在创建图片</h3>
                <div class="placeholder">
                    <div class="spinner"></div>
                </div>
            </div>
            <!-- 图片生成 -->
            <div v-else>
                <h3 class="result-text">图片已创建</h3>
                <img :src="item.image" class="thumbnail" @click="openModal(index)" />
            </div>
        </div>

        <div class="modal" v-if="showModal" @click="showModal = false">
            <img :src="items[modalIndex].image" class="full-img" />
        </div>
    </div>
</template>


<script>
import { generatePainting } from '../services/api'

export default {
    data() {
        return {
            inputText: '',
            items: [],
            showModal: false,
            modalIndex: 0 // 当前 modal 显示的图片索引
        }
    },
    methods: {
        handleEnter(e) {
            // Shift + Enter 换行
            if (e.shiftKey) return;

            // 普通 Enter = 发送
            this.generate();
        },

        scrollToBottom() {
            this.$nextTick(() => {
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            });
        },

        async generate() {
            if (!this.inputText.trim()) return;

            const index = this.items.length;

            this.items.push({ loading: true, image: null, text: this.inputText });
            this.inputText = '';

            // ⭐⭐ 重置 textarea 高度 ⭐⭐
            this.$nextTick(() => {
                const ta = this.$refs.textarea;
                ta.style.height = "21px";   // 单行高度
            });

            this.scrollToBottom();

            await new Promise(r => setTimeout(r, 500));

            try {
                const res = await generatePainting(this.items[index].text);
                this.items[index].image = `data:image/png;base64,${res.data.image}`;
            } catch (err) {
                console.error(err);
                this.items[index].image = null;
            }
            this.items[index].loading = false;

            this.scrollToBottom();
        },



        openModal(index) {
            this.modalIndex = index;
            this.showModal = true;
        },
        autoResize() {
            const ta = this.$refs.textarea
            const lineHeight = 21;
            const maxHeight = 100;

            ta.style.height = lineHeight + "px";
            const newHeight = Math.min(ta.scrollHeight, maxHeight);
            ta.style.height = Math.max(newHeight, lineHeight) + "px";
        }
    }

}
</script>


<style>
/* 整个网页 */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f5f7fa;
    /* 浅灰蓝背景 */
    color: #333;
    margin: 0;
    padding: 0;
}

/* 外层大盒子 */
.container {
    max-width: 700px;
    min-height: 630px;
    /* 初始高度，页面加载时就占据 */
    margin: 15px auto;
    padding: 10px 25px 60px 25px;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transition: min-height 0.3s ease;
    /* 可选，拉伸动画 */
}

/* 大标题 */
h2 {
    font-size: 36px;
    /* 字号 */
    font-weight: bold;
    /* 字重，加粗 */
    color: #333;
    /* 文字颜色 */
    margin-top: 0px;
    margin-bottom: 20px;
    /* 下方间距 */
    text-align: center;
    /* 居中对齐 */
    font-family: "Microsoft YaHei", sans-serif;
    /* 字体 */
}

/* 用户输入内容展示 */
.user-text-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
    /* 靠右 */
}

/* 用户输入文本 */
.user-text {
    display: inline-block;
    /* 宽度随内容自适应 */
    max-width: 60%;
    padding: 8px 12px;
    background-color: #efefef;
    color: #000000;
    border-radius: 16px;
    font-size: 14px;
    font-family: "Inter", "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-weight: 440;
    word-break: break-word;
    white-space: pre-wrap;
    /* 保留换行 */
}

/* "正在创建图片" */
.loading-text {
    animation: fade 1.5s infinite ease-in-out;
    color: #777;
    font-weight: bold;
    margin-bottom: 10px;
}

/* “正在创建图片”小标题 */
h3 {
    font-family: "Inter", "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    /* 微软雅黑 */
    font-size: 14px;
    font-weight: 500;
    /* 字体大小 */
    margin: 10px 0;
    /* 上下间距统一 */
}

/* 文字呼吸效果动画 */
@keyframes fade {
    0% {
        opacity: 0.3;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.3;
    }
}

/* 占位框 */
.placeholder {
    width: 320px;
    height: 320px;
    background-color: #f3f3f3;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #999;
    font-size: 18px;
    border-radius: 6px;
    position: relative;
}

/* 加载图片时占位框里旋转的圈 */
.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #dddcdcbd;
    /* 背景色 */
    border-top: 5px solid #6b6f72;
    /* 旋转的前景色 */
    border-radius: 50%;
    /* 圆形 */
    animation: spin 1s linear infinite;
    margin-bottom: 20px;

    position: absolute;
    /* 绝对定位到占位框内部 */
    /* top: 50%;                垂直中心 */
    /* left: 50%;               水平中心 */
    /* transform: translate(-50%, -50%); 修正偏移，让中心对齐 */
}

/* 加载图片时占位框里旋转的圈旋转的动画 */
@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

/* “图片已创建”小标题 */
h3.result-text {
    color: #6d6d6d;
    /* 调暗一点的颜色 */
    font-family: "Inter", "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-weight: 500;
    /* 调细 */
    font-size: 14px;
    /* 字体大小 */

    margin: 10px 0;
    /* 根据需要调整上下间距 */
}

/* 缩略图 */
.thumbnail {
    /*缩略图样式*/
    width: 320px;
    height: 320px;
    object-fit: cover;
    /* 保持裁剪效果 */
    cursor: pointer;
    border-radius: 6px;
    transition: transform .2s;
}

.thumbnail:hover {
    transform: scale(1.05);
}

/* 渲染全屏弹窗 */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
}

/* 全屏弹窗中具体图片 */
.full-img {
    max-width: 90%;
    max-height: 90%;
    border-radius: 3px;
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.3);
}

/* 输入部分外面套的box：输入框+按钮*/
.input-bar {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 620px;

    /* 背景与阴影 */
    background: #ffffff;
    border-radius: 24px;
    /* box-shadow:
        0 2px 6px rgba(0, 0, 0, 0.05),
        0 4px 24px rgba(0, 0, 0, 0.12); */

    padding: 13px 44px 12px 16px;
    /* 右侧留给按钮 */

    display: flex;
    align-items: center;
    z-index: 999;

    /* ChatGPT 的那种玻璃柔和感 */
    border: 1px solid #e5e7eb;
    backdrop-filter: blur(6px);
}

/* 文字输入框 textarea */
.input-bar textarea {
    width: 100%;
    resize: none;
    /* border: none; */

    font-size: 14px;
    font-family: "Microsoft YaHei", 微软雅黑, sans-serif;
    color: #111;
    line-height: 1.5;

    background: transparent;

    max-height: 100px;
    overflow-y: auto;
    /* 超过会出现滚动条 */


    /* 让未输入时只有一行高度 */
    /* padding: 6px 0; */
    padding: 0 2px;
    height: 21px;
    min-height: 21px;
    box-sizing: border-box;
    border: none;
}

.input-bar textarea:focus {
    outline: none;
    /* 禁用默认焦点边框 */
    /* 如果你想添加自定义高亮效果，可以在这里加 border 或 box-shadow */
}

.input-bar textarea::-webkit-scrollbar {
    width: 8px;
    /* 滚动条宽度 */
}

.input-bar textarea::-webkit-scrollbar-track {
    background: #f1f1f1;
    /* 滚动条轨道 */
    border-radius: 4px;
}

.input-bar textarea::-webkit-scrollbar-thumb {
    background: #888;
    /* 滚动条颜色 */
    border-radius: 4px;
}

.input-bar textarea::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* 按钮 */
.send-button {
    position: absolute;
    right: 8px;
    bottom: 8px;

    width: 30px;
    height: 30px;
    border-radius: 50%;
    /* 圆形 */
    background-color: #000;
    /* 黑色 */
    color: #fff;
    /* 白色文字 */
    border: none;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;
    font-weight: 900;
    /* 加粗 */
    padding: 0;
    outline: none;
    transition: background 0.2s ease;

    padding-bottom: 5px;

}

.send-button:hover {
    background-color: #333;
    /* 悬停稍微变暗 */
}
</style>