
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
} from 'react-native';

// 메시지 객체의 타입을 정의합니다.
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
}

// 로딩 인디케이터 컴포넌트
const LoadingIndicator = () => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const dotAnimation = setInterval(() => {
      setDots(prevDots => (prevDots.length < 3 ? prevDots + '.' : ''));
    }, 400);

    return () => clearInterval(dotAnimation);
  }, []);

  return (
    <View style={styles.botMessage}>
      <Text style={styles.botMessageText}>응답을 기다리는 중{dots}</Text>
    </View>
  );
};

const App = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  // 앱 종료 처리 함수 (Android 전용)
  const handleExitApp = () => {
    if (Platform.OS === 'android') {
      BackHandler.exitApp();
    } else {
      Alert.alert('알림', 'iOS에서는 앱을 직접 종료할 수 없습니다. 홈 화면으로 이동하여 앱을 종료해주세요.');
    }
  };

  // 메시지 전송 처리 함수
  const handleSendMessage = async () => {
    if (inputText.trim().length === 0 || isLoading) {
      return;
    }

    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
    };

    setMessages(prevMessages => [...prevMessages, newMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ msg: inputText }),
      });

      const data = await response.json();
      const botResponseText = data.llm_response || data.response || '죄송합니다, 응답을 처리할 수 없습니다.';

      const botMessage: Message = {
        id: Date.now().toString() + '-bot',
        text: botResponseText,
        sender: 'bot',
      };
      setMessages(prevMessages => [...prevMessages, botMessage]);

    } catch (error) {
      console.error('Error fetching bot response:', error);
      const errorMessage: Message = {
        id: Date.now().toString() + '-error',
        text: '오류가 발생했습니다. 다시 시도해주세요.',
        sender: 'bot',
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd();
    }
  }, [messages, isLoading]);

  const renderMessage = ({ item }: { item: Message }) => (
    <View
      style={[
        styles.messageContainer,
        item.sender === 'user' ? styles.userMessageContainer : styles.botMessageContainer,
      ]}
    >
      <View style={item.sender === 'user' ? styles.userMessage : styles.botMessage}>
        <Text style={item.sender === 'user' ? styles.userMessageText : styles.botMessageText}>
          {item.text}
        </Text>
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
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <FlatList
          ref={flatListRef}
          data={[...messages, ...(isLoading ? [{ id: 'loading', text: '', sender: 'bot' }] : [])]}
          renderItem={({ item }) => item.id === 'loading' ? <LoadingIndicator /> : renderMessage({ item })}
          keyExtractor={item => item.id}
          style={styles.messageList}
          contentContainerStyle={{ paddingBottom: 10 }}
        />
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="메시지를 입력하세요..."
            placeholderTextColor="#999"
            returnKeyType="send"
          />
          <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage} disabled={isLoading}>
            <Text style={styles.sendButtonText}>전송</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
    backgroundColor: 'white',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  exitButton: {
    padding: 5,
  },
  exitButtonText: {
    fontSize: 20,
    color: '#888',
    fontWeight: 'bold',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  messageList: {
    flex: 1,
    paddingHorizontal: 10,
  },
  messageContainer: {
    marginVertical: 5,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  botMessageContainer: {
    alignItems: 'flex-start',
  },
  userMessage: {
    backgroundColor: '#007bff',
    borderRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 15,
    maxWidth: '80%',
  },
  botMessage: {
    backgroundColor: '#e9e9eb',
    borderRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 15,
    maxWidth: '80%',
  },
  userMessageText: {
    color: 'white',
    fontSize: 16,
  },
  botMessageText: {
    color: 'black',
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#ddd',
    backgroundColor: 'white',
  },
  input: {
    flex: 1,
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 15,
    backgroundColor: '#fff',
    marginRight: 10,
  },
  sendButton: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    backgroundColor: '#007bff',
    borderRadius: 20,
  },
  sendButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loadingText: {
    fontStyle: 'italic',
    color: '#666',
  },
});

export default App;
