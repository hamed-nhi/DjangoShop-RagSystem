// document.addEventListener('DOMContentLoaded', function() {
//     // --- پیدا کردن تمام عناصر مورد نیاز ---
//     const chatToggle = document.getElementById('chat-toggle');
//     const chatContainer = document.getElementById('chat-container');
//     const chatClose = document.getElementById('chat-close');
//     const chatMinimize = document.getElementById('chat-minimize');
//     const chatInput = document.getElementById('chat-input');
//     const chatSend = document.getElementById('chat-send');
//     const chatMessages = document.getElementById('chat-messages');
//     const typingIndicator = document.getElementById('typing-indicator');
//     const floatingChatDiv = document.querySelector('.floating-chat');
//     // --- جدید: پیدا کردن لینک صفحه کامل ---
//     const fullChatLink = document.getElementById('full-chat-link');

//     if (!chatToggle || !chatContainer || !floatingChatDiv) {
//         console.error('Chat widget essential elements not found. Script terminated.');
//         return;
//     }

//     let isChatOpen = false;
//     let isWaitingForResponse = false;
//     let chatUrl = '';
//     // --- جدید: متغیری برای ذخیره شناسه مکالمه ---
//     let currentWidgetConversationId = null;

//     // --- اعتبارسنجی URL ---
//     const chatUrlBase = floatingChatDiv.dataset.chatUrl;
//     if (!chatUrlBase || chatUrlBase === 'undefined' || chatUrlBase.trim() === '') {
//         console.error('ERROR: data-chat-url is not configured in the HTML.');
//         if (chatInput) {
//             chatInput.placeholder = 'چت غیرفعال است.';
//             chatInput.disabled = true;
//         }
//         if (chatSend) chatSend.disabled = true;
//     } else {
//         chatUrl = chatUrlBase; // آدرس پایه را ذخیره می‌کنیم
//     }

//     // --- اتصال رویدادها (Event Listeners) ---
//     chatToggle.addEventListener('click', toggleChat);
//     if (chatClose) chatClose.addEventListener('click', closeChat);
//     if (chatMinimize) chatMinimize.addEventListener('click', closeChat);
    
//     async function toggleChat() {
//         if (!isChatOpen) {
//             await openChat();
//         } else {
//             closeChat();
//         }
//     }

//     async function openChat() {
//         chatContainer.classList.add('active');
//         isChatOpen = true;
//         if (chatInput) chatInput.focus();
        
//         // اگر شناسه مکالمه را نداریم، آن را از سرور درخواست می‌کنیم
//         if (!currentWidgetConversationId) {
//             await initializeWidgetSession();
//         }
//     }

//     function closeChat() {
//         chatContainer.classList.remove('active');
//         isChatOpen = false;
//     }

//     // رویدادهای مربوط به ارسال پیام
//     if (chatSend && !chatSend.disabled) {
//         chatSend.addEventListener('click', sendMessage);
//     }
//     if (chatInput && !chatInput.disabled) {
//         chatInput.addEventListener('keypress', function(e) {
//             if (e.key === 'Enter') sendMessage();
//         });
//     }

//     // --- تابع جدید برای دریافت شناسه مکالمه ---
//     async function initializeWidgetSession() {
//         try {
//             // یک درخواست GET برای گرفتن یا ایجاد مکالمه ارسال می‌کنیم
//             const response = await fetch(`${chatUrl}?widget=true`, {
//                 method: 'GET',
//                 headers: { 'X-Requested-With': 'XMLHttpRequest' }
//             });
//             if (!response.ok) throw new Error('Failed to initialize session');
//             const data = await response.json();
            
//             currentWidgetConversationId = data.conversation_id;
//             console.log('Widget session initialized with ID:', currentWidgetConversationId);

//             // لینک صفحه کامل را با شناسه جدید به‌روزرسانی می‌کنیم
//             if (fullChatLink && currentWidgetConversationId) {
//                 const baseUrl = chatUrl.endsWith('/') ? chatUrl : chatUrl + '/';
//                 fullChatLink.href = `${baseUrl}${currentWidgetConversationId}/`;
//             }
//         } catch (error) {
//             console.error("Could not initialize widget session:", error);
//             addMessage('خطا در برقراری ارتباط اولیه با سرور.', 'bot');
//             if(chatInput) chatInput.disabled = true;
//             if(chatSend) chatSend.disabled = true;
//         }
//     }

//     // --- تغییر: تابع sendMessage اکنون از شناسه مکالمه استفاده می‌کند ---
//     async function sendMessage() {
//         const message = chatInput.value.trim();
//         if (!message || isWaitingForResponse) return;

//         if (!currentWidgetConversationId) {
//             await initializeWidgetSession();
//             if(!currentWidgetConversationId) {
//                  addMessage('خطا: ارتباط برقرار نشد. پنجره را بسته و دوباره باز کنید.', 'bot');
//                  return;
//             }
//         }

//         addMessage(message, 'user');
//         chatInput.value = '';
//         isWaitingForResponse = true;
//         if (typingIndicator) typingIndicator.classList.add('active');
//         scrollToBottom();

//         // آدرس URL برای ارسال پیام باید به مکالمه خاص اشاره کند
//         const postUrl = `${chatUrl}${currentWidgetConversationId}/?widget=true`;

//         try {
//             const response = await fetch(postUrl, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-Requested-With': 'XMLHttpRequest',
//                     'X-CSRFToken': getCSRFToken(),
//                 },
//                 body: JSON.stringify({ message: message })
//             });

//             if (!response.ok) {
//                 const errorData = await response.json().catch(() => ({ error: 'خطای ناشناخته در سرور.' }));
//                 addMessage(errorData.error || 'خطا در ارتباط با سرور.', 'bot');
//                 throw new Error(`Server error: ${response.status}`);
//             }
            
//             const reader = response.body.getReader();
//             const decoder = new TextDecoder();
            
//             const messageDiv = createMessageElement('bot');
//             const responseElement = messageDiv.querySelector('.streaming-response');
//             if (chatMessages) chatMessages.appendChild(messageDiv);
            
//             let botResponse = '';
//             while (true) {
//                 const { value, done } = await reader.read();
//                 if (done) break;

//                 const chunk = decoder.decode(value, { stream: true });
//                 botResponse += chunk;
//                 if (responseElement) responseElement.textContent = botResponse;
//                 scrollToBottom();
//             }
//         } catch (error) {
//             console.error('Chat Error:', error.message);
//         } finally {
//             if (typingIndicator) typingIndicator.classList.remove('active');
//             isWaitingForResponse = false;
//         }
//     }
    
//     function createMessageElement(sender) {
//         const messageDiv = document.createElement('div');
//         messageDiv.className = `message ${sender}`;
//         const contentHtml = sender === 'bot' ? '<p class="streaming-response"></p>' : '<p></p>';
//         messageDiv.innerHTML = `
//             <div class="message-avatar"><i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i></div>
//             <div class="message-content">${contentHtml}</div>
//         `;
//         return messageDiv;
//     }
    
//     function addMessage(text, sender) {
//         const messageDiv = createMessageElement(sender);
//         const p = messageDiv.querySelector('p');
//         if (p) p.textContent = text;
//         if (chatMessages) {
//             chatMessages.appendChild(messageDiv);
//             scrollToBottom();
//         }
//     }

//     function scrollToBottom() {
//         if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
//     }

//     function getCSRFToken() {
//         const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
//         return cookie ? cookie.split('=')[1] : '';
//     }
// });

