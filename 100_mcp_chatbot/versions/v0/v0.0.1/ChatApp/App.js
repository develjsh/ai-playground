import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  BackHandler,
  Alert,
  Image,
} from 'react-native';
import DocumentPicker from 'react-native-document-picker';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef(null);

  const handleExitApp = () => {
    if (Platform.OS === 'android') {
      BackHandler.exitApp();
    } else {
      Alert.alert('알림', 'iOS에서는 앱을 직접 종료할 수 없습니다. 홈 화면으로 이동하여 앱을 종료해주세요.');
    }
  };

  const addMessage = (message) => {
    setMessages(prevMessages => [...prevMessages, message]);
  };

  const handleSendMessage = async () => {
    const trimmedInput = inputText.trim();
    if (trimmedInput.length === 0) return;

    addMessage({ id: Date.now().toString(), text: trimmedInput, sender: 'user' });
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ msg: trimmedInput }),
      });
      const data = await response.json();
      const botResponseText = data.llm_response || '죄송합니다, 응답을 처리할 수 없습니다.';
      addMessage({ id: Date.now().toString() + '-bot', text: botResponseText, sender: 'bot' });
    } catch (error) {
      console.error('Error fetching text response:', error);
      addMessage({ id: Date.now().toString() + '-error', text: '텍스트 메시지 전송 중 오류가 발생했습니다.', sender: 'bot' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttachment = async () => {
    try {
      const res = await DocumentPicker.pickSingle({ type: [DocumentPicker.types.allFiles] });

      addMessage({ id: Date.now().toString(), text: `파일 보내는 중: ${res.name}`, sender: 'user' });
      setIsLoading(true);

      const formData = new FormData();
      formData.append('file', { uri: res.uri, type: res.type, name: res.name });

      const uploadResponse = await fetch('http://localhost:8001/upload', {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const responseData = await uploadResponse.json();
      if (!uploadResponse.ok) throw new Error(responseData.detail || 'File upload failed');

      const botMessage = {
        id: Date.now().toString() + '-bot',
        sender: 'bot',
        // Use original_filename for the text, and file_url for the image
        text: responseData.file_url ? `이미지: ${responseData.original_filename}` : responseData.info,
        imageUrl: responseData.file_url || null,
      };
      addMessage(botMessage);

    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        console.log('User cancelled the picker');
      } else {
        console.error('Attachment Error: ', err);
        addMessage({ id: Date.now().toString() + '-error', text: '파일 업로드 중 오류가 발생했습니다.', sender: 'bot' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    flatListRef.current?.scrollToEnd();
  }, [messages]);

  const renderMessage = ({ item }) => (
    <View style={[styles.messageContainer, item.sender === 'user' ? styles.userMessageContainer : styles.botMessageContainer]}>
      <View style={[styles.messageBubble, item.sender === 'user' ? styles.userMessage : styles.botMessage]}>
        {item.text && (
          <Text style={item.sender === 'user' ? styles.userMessageText : styles.botMessageText}>
            {item.text}
          </Text>
        )}
        {item.imageUrl && (
          <Image source={{ uri: item.imageUrl }} style={styles.chatImage} resizeMode="contain" />
        )}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>MCP Chatbot</Text>
        <TouchableOpacity onPress={handleExitApp} style={styles.exitButton}>
          <Text style={styles.exitButtonText}>X</Text>
        </TouchableOpacity>
      </View>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.keyboardAvoidingView}>
        <FlatList
          data={messages}
          renderItem={renderMessage}
          keyExtractor={item => item.id}
          style={styles.messageList}
          contentContainerStyle={{ paddingBottom: 10 }} 
        />
        {isLoading && (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>처리 중...</Text>
          </View>
        )}
        <View style={styles.inputContainer}>
          <TouchableOpacity onPress={handleAttachment} style={styles.attachmentButton} disabled={isLoading}>
            <Text style={styles.attachmentButtonText}>📎</Text>
          </TouchableOpacity>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="메시지를 입력하세요..."
            placeholderTextColor="#999"
          />
          <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage} disabled={!inputText.trim() || isLoading}>
            <Text style={styles.sendButtonText}>전송</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 15, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#ddd', backgroundColor: 'white' },
  headerTitle: { fontSize: 20, fontWeight: 'bold' },
  exitButton: { padding: 5 },
  exitButtonText: { fontSize: 20, color: '#888', fontWeight: 'bold' },
  keyboardAvoidingView: { flex: 1 },
  messageList: { flex: 1, paddingHorizontal: 10 },
  messageContainer: { marginVertical: 5 },
  userMessageContainer: { alignItems: 'flex-end' },
  botMessageContainer: { alignItems: 'flex-start' },
  messageBubble: { borderRadius: 20, padding: 10, maxWidth: '80%' },
  userMessage: { backgroundColor: '#007bff' },
  botMessage: { backgroundColor: '#e9e9eb' },
  userMessageText: { color: 'white', fontSize: 16 },
  botMessageText: { color: 'black', fontSize: 16 },
  chatImage: { width: 200, height: 200, borderRadius: 10 },
  inputContainer: { flexDirection: 'row', alignItems: 'center', padding: 10, borderTopWidth: 1, borderTopColor: '#ddd', backgroundColor: 'white' },
  input: { flex: 1, height: 40, borderColor: '#ccc', borderWidth: 1, borderRadius: 20, paddingHorizontal: 15, backgroundColor: '#fff', marginRight: 10 },
  sendButton: { justifyContent: 'center', alignItems: 'center', paddingHorizontal: 20, height: 40, backgroundColor: '#007bff', borderRadius: 20 },
  sendButtonText: { color: 'white', fontSize: 16, fontWeight: 'bold' },
  attachmentButton: { padding: 5, marginRight: 5 },
  attachmentButtonText: { fontSize: 24, color: '#007bff' },
  loadingContainer: { alignItems: 'center', padding: 10 },
  loadingText: { fontStyle: 'italic', color: '#666' },
});

export default App;