"use client"

import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden"
import Link from "next/link"
import { Phone, Users, MousePointerClick, Mic, MicOff } from "lucide-react"
import { motion } from "framer-motion"
import { useState, useEffect, useRef } from "react"

interface VoiceCommandModalProps {
  isOpen: boolean
  onOpenChange: (isOpen: boolean) => void
}

export function VoiceCommandModal({ isOpen, onOpenChange }: VoiceCommandModalProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognizedCommand, setRecognizedCommand] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Initialize speech recognition when the modal opens
  useEffect(() => {
    if (isOpen) {
      // Check if browser supports SpeechRecognition
      if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
          setIsListening(true);
          setTranscript('');
          setRecognizedCommand(null);
        };
        
        recognition.onresult = (event) => {
          const current = event.resultIndex;
          const result = event.results[current];
          const transcriptText = result[0].transcript.trim().toLowerCase();
          setTranscript(transcriptText);
          
          // Process commands when we have a final result
          if (result.isFinal) {
            processCommand(transcriptText);
          }
        };
        
        recognition.onerror = (event) => {
          console.error('Speech recognition error', event.error);
          setIsListening(false);
        };
        
        recognition.onend = () => {
          setIsListening(false);
          // Restart recognition if modal is still open and no command was recognized
          if (isOpen && !recognizedCommand) {
            recognition.start();
          }
        };
        
        recognitionRef.current = recognition;
        recognition.start();
      }
    } else {
      // Stop recognition when modal closes
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
    };
  }, [isOpen, recognizedCommand]);
  
  const processCommand = (command: string) => {
    // Simple command matching logic
    if (command.includes('record call') || command.includes('call recording')) {
      setRecognizedCommand('call');
      setTimeout(() => {
        onOpenChange(false);
        window.location.href = '/call/1';
      }, 1000);
    } else if (command.includes('record meeting') || command.includes('meeting recording')) {
      setRecognizedCommand('meeting');
      setTimeout(() => {
        onOpenChange(false);
        window.location.href = '/call/new';
      }, 1000);
    } else if (command.includes('automate') || command.includes('task') || command.includes('automation')) {
      setRecognizedCommand('task');
      setTimeout(() => {
        onOpenChange(false);
        window.location.href = '/call/3';
      }, 1000);
    }
  };
  
  const toggleListening = () => {
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
    } else if (!isListening && recognitionRef.current) {
      setTranscript('');
      setRecognizedCommand(null);
      recognitionRef.current.start();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="bg-black/80 backdrop-blur-lg border-0 text-white p-0 w-full h-full max-w-full sm:max-w-lg sm:h-auto sm:rounded-2xl">
        <VisuallyHidden>
          <DialogTitle>Voice Command Interface</DialogTitle>
        </VisuallyHidden>
        <div className="flex flex-col items-center justify-center p-8 sm:p-12 h-full">
          <h2 className="text-2xl font-bold text-white mb-6 tracking-tight">Say It, Saydo It.</h2>

          <div className="relative w-48 h-48 flex items-center justify-center mb-8">
            {isListening && [...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-full h-full rounded-full border border-purple-500/30"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 2,
                  ease: "easeInOut",
                  repeat: Number.POSITIVE_INFINITY,
                  delay: i * 0.3,
                }}
              />
            ))}
            <motion.div
              className={`w-24 h-24 rounded-full shadow-2xl flex items-center justify-center ${isListening ? 'bg-purple-600 shadow-purple-600/50' : 'bg-gray-700 shadow-gray-700/30'}`}
              animate={{ scale: isListening ? [1, 1.05, 1] : 1 }}
              transition={{ duration: 1.5, ease: "easeInOut", repeat: isListening ? Number.POSITIVE_INFINITY : 0 }}
              onClick={toggleListening}
            >
              {isListening ? <Mic className="w-8 h-8 text-white" /> : <MicOff className="w-8 h-8 text-gray-300" />}
            </motion.div>
          </div>

          <div className="text-center mb-8">
            {recognizedCommand ? (
              <p className="text-green-400">Command recognized: {recognizedCommand}</p>
            ) : transcript ? (
              <p className="text-gray-300">"{transcript}"</p>
            ) : (
              <p className="text-gray-400">{isListening ? 'Listening for a command...' : 'Click the microphone to start'}</p>
            )}
          </div>

          <div className="flex items-center justify-center gap-4 sm:gap-6">
            <Link
              href="/call/1"
              className="flex flex-col items-center gap-2 text-gray-300 hover:text-white transition-colors"
              onClick={() => onOpenChange(false)}
            >
              <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center bg-gray-800/50">
                <Phone className="w-5 h-5" />
              </div>
              <span className="text-xs">Record Call</span>
            </Link>
            <Link
              href="/call/new"
              className="flex flex-col items-center gap-2 text-gray-300 hover:text-white transition-colors"
              onClick={() => onOpenChange(false)}
            >
              <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center bg-gray-800/50">
                <Users className="w-5 h-5" />
              </div>
              <span className="text-xs">Record Meeting</span>
            </Link>
            <Link
              href="/call/3"
              className="flex flex-col items-center gap-2 text-gray-300 hover:text-white transition-colors"
              onClick={() => onOpenChange(false)}
            >
              <div className="w-12 h-12 rounded-full border border-gray-700 flex items-center justify-center bg-gray-800/50">
                <MousePointerClick className="w-5 h-5" />
              </div>
              <span className="text-xs">Automate Task</span>
            </Link>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
