import { useState, useEffect } from 'react';
import { triggerImageGeneration, checkImageGenerationStatus } from '@/services/api';

interface ImageGenerationState {
  isGenerating: boolean;
  imageUrl: string | null;
  error: string | null;
  taskId: string | null;
}

export const useImageGeneration = (playerName: string, sessionId?: string, autoStart = false) => {
  const [state, setState] = useState<ImageGenerationState>({
    isGenerating: false,
    imageUrl: null,
    error: null,
    taskId: null
  });

  const startGeneration = async () => {
    try {
      setState(prev => ({ ...prev, isGenerating: true, error: null }));
      
      const result = await triggerImageGeneration(playerName, sessionId);
      
      if (result.success && result.taskId) {
        setState(prev => ({ ...prev, taskId: result.taskId! }));
        
        // If image is immediately available (unlikely but possible)
        if (result.imageUrl) {
          setState(prev => ({ 
            ...prev, 
            imageUrl: result.imageUrl!, 
            isGenerating: false 
          }));
          return;
        }
        
        // Start polling for status
        pollForResult(result.taskId);
      } else {
        setState(prev => ({ 
          ...prev, 
          isGenerating: false, 
          error: result.error || 'Failed to start image generation' 
        }));
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isGenerating: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }));
    }
  };

  const pollForResult = async (taskId: string) => {
    let attempts = 0;
    const maxAttempts = 60; // 2 minutes with 2-second intervals
    
    const poll = async () => {
      try {
        attempts++;
        const status = await checkImageGenerationStatus(taskId);
        
        if (status.status === 'completed' && status.imageUrl) {
          setState(prev => ({ 
            ...prev, 
            imageUrl: status.imageUrl!, 
            isGenerating: false 
          }));
        } else if (status.status === 'failed') {
          setState(prev => ({ 
            ...prev, 
            isGenerating: false, 
            error: status.error || 'Image generation failed' 
          }));
        } else if (attempts < maxAttempts) {
          // Continue polling
          setTimeout(poll, 2000);
        } else {
          // Timeout
          setState(prev => ({ 
            ...prev, 
            isGenerating: false, 
            error: 'Image generation timed out' 
          }));
        }
      } catch (error) {
        setState(prev => ({ 
          ...prev, 
          isGenerating: false, 
          error: error instanceof Error ? error.message : 'Polling error' 
        }));
      }
    };
    
    poll();
  };

  const reset = () => {
    setState({
      isGenerating: false,
      imageUrl: null,
      error: null,
      taskId: null
    });
  };

  // Auto-start if requested
  useEffect(() => {
    if (autoStart && playerName) {
      startGeneration();
    }
  }, [autoStart, playerName, sessionId]);

  return {
    ...state,
    startGeneration,
    reset
  };
};
