import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  Paper,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Divider,
  Alert
} from '@mui/material';
import { OpenAI } from 'openai';
import { ChatCompletionMessageParam } from 'openai/resources/chat/completions';

// Theme mit Bordeaux-Rot
const theme = createTheme({
  palette: {
    primary: {
      main: '#800020',
    },
  },
});

function App() {
  const [traumjob, setTraumjob] = useState('');
  const [interessen, setInteressen] = useState('');
  const [staerken, setStaerken] = useState('');
  const [chatStarted, setChatStarted] = useState(false);
  const [messages, setMessages] = useState<ChatCompletionMessageParam[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const openai = new OpenAI({
    apiKey: process.env.REACT_APP_OPENAI_API_KEY,
    dangerouslyAllowBrowser: true
  });

  const handleSubmit = async () => {
    if (!traumjob || !interessen || !staerken) {
      alert('Bitte fülle alle Felder aus.');
      return;
    }

    setIsLoading(true);

    try {
      const basePrompt: ChatCompletionMessageParam = {
        role: "system",
        content: `
          Du bist ein inspirierender KI-Coach für Berufsorientierung.
          Deine Aufgabe ist es, basierend auf den Interessen und Stärken des Nutzers passende Berufsinspirationen zu geben.
          Stelle keine Diagnosen und gib keine vorschnellen Ratschläge. 
          Fokussiere dich darauf, neue Perspektiven zu eröffnen und Denkanstöße zu geben.
        `
      };

      const inspirationPrompt: ChatCompletionMessageParam = {
        role: "user",
        content: `
          Basierend auf folgenden Informationen, gib 5 konkrete Berufsinspirationen:
          
          Traumjob-Kriterien: ${traumjob}
          Top 3 Interessen: ${interessen}
          Top 3 Stärken: ${staerken}
          
          Für jeden Beruf:
          1. Nenne den Berufstitel
          2. Erkläre kurz, warum dieser Beruf passen könnte
          3. Gib 2-3 Kernaufgaben des Berufs
          
          Formatiere die Antwort übersichtlich mit Emojis und Absätzen.
        `
      };

      const completion = await openai.chat.completions.create({
        messages: [basePrompt, inspirationPrompt],
        model: "gpt-4",
      });

      const response = completion.choices[0].message.content;
      if (response) {
        setMessages([
          basePrompt,
          inspirationPrompt,
          { role: "assistant", content: response }
        ]);
        setChatStarted(true);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Ein Fehler ist aufgetreten. Bitte versuche es später erneut.');
    }

    setIsLoading(false);
  };

  const handleChat = async () => {
    if (!userInput.trim()) return;

    const userMessage: ChatCompletionMessageParam = {
      role: "user",
      content: userInput
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setUserInput('');
    setIsLoading(true);

    try {
      const completion = await openai.chat.completions.create({
        messages: newMessages,
        model: "gpt-4",
      });

      const response = completion.choices[0].message.content;
      if (response) {
        const assistantMessage: ChatCompletionMessageParam = {
          role: "assistant",
          content: response
        };
        setMessages([...newMessages, assistantMessage]);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Ein Fehler ist aufgetreten. Bitte versuche es später erneut.');
    }

    setIsLoading(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          🎯 Mein Mutiger Weg Berufsinspirationen
        </Typography>

        <Typography variant="body1" paragraph>
          Willkommen! 💙 Hier bekommst du neue Perspektiven für deine Berufswahl.
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Deine Berufswünsche und Stärken
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Was sind deine wichtigsten Kriterien für deinen Traumjob?"
            value={traumjob}
            onChange={(e) => setTraumjob(e.target.value)}
            margin="normal"
            helperText="⚠️ Bitte gib hier keine personenbezogenen Daten ein (z. B. deinen Namen, deine Adresse oder deine Schule)"
          />

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Was sind deine Top 3 Interessen?"
            value={interessen}
            onChange={(e) => setInteressen(e.target.value)}
            margin="normal"
            helperText="⚠️ Bitte gib hier keine personenbezogenen Daten ein (z. B. deinen Namen, deine Adresse oder deine Schule)"
          />

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Was sind deine Top 3 Stärken?"
            value={staerken}
            onChange={(e) => setStaerken(e.target.value)}
            margin="normal"
            helperText="⚠️ Bitte gib hier keine personenbezogenen Daten ein (z. B. deinen Namen, deine Adresse oder deine Schule)"
          />

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button 
              variant="contained" 
              onClick={handleSubmit}
              disabled={isLoading || !traumjob || !interessen || !staerken}
            >
              🎯 Berufsinspirationen erhalten
            </Button>
          </Box>
        </Paper>

        {chatStarted && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              💬 Dein Feedback
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Box sx={{ mb: 3 }}>
              {messages.filter(msg => msg.role !== 'system').map((message, index) => (
                <Box
                  key={index}
                  sx={{
                    mb: 2,
                    p: 2,
                    backgroundColor: message.role === 'assistant' ? '#f5f5f5' : '#e3f2fd',
                    borderRadius: 2
                  }}
                >
                  <Typography variant="body1" whiteSpace="pre-wrap">
                    {typeof message.content === 'string' ? message.content : ''}
                  </Typography>
                </Box>
              ))}
            </Box>

            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                label="Was denkst du zu deinen Berufsinspirationen?"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                disabled={isLoading}
              />
              <Button 
                variant="contained" 
                onClick={handleChat}
                disabled={isLoading || !userInput.trim()}
              >
                Senden
              </Button>
            </Box>
          </Paper>
        )}
      </Container>
    </ThemeProvider>
  );
}

export default App;
