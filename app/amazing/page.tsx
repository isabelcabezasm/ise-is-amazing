"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Plus, Clock, Wifi, WifiOff, Download, AlertCircle } from "lucide-react";
import { AMAZING_API_URL } from "@/lib/api-config";

// Types for our amazing items
interface AmazingItem {
  id: string;
  text: string;
  language: string;
  reps: number;
}

export default function YouAreAmazingPage() {
  const [items, setItems] = useState<AmazingItem[]>([]);
  const [newItemText, setNewItemText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load initial amazing items and setup polling for updates
  useEffect(() => {
    // Function to load amazing items
    const loadAmazingItems = () => {
      fetch(AMAZING_API_URL)
        .then(res => {
          if (!res.ok) throw new Error('API not available');
          return res.json();
        })
        .then(data => {
          setItems(data.items);
          setIsConnected(true);
        })
        .catch(error => {
          console.error('Error loading amazing items:', error);
          setIsConnected(false);
          // Fallback to simulated data when API is not available
          setItems([
            {
              id: "1",
              text: "You are amazing!",
              language: "English",
              reps: 1,
            },
          ]);
        });
    };

    // Load initial amazing items
    loadAmazingItems();

    // Poll for updates every 2 seconds (simulating real-time)
    const pollInterval = setInterval(() => {
      loadAmazingItems(); // Always try to load, regardless of connection status
    }, 2000);

    // Cleanup on unmount
    return () => {
      clearInterval(pollInterval);
    };
  }, []); // Removed isConnected dependency to avoid infinite loops

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemText.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setError(null); // Clear any previous errors
    
    try {
      const response = await fetch(AMAZING_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: newItemText.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.duplicate) {
          // Item already exists, update the existing item with new reps count
          setItems(prevItems => 
            prevItems.map(item => 
              item.id === data.item.id ? data.item : item
            )
          );
        } else {
          // New item was created, reload items to get fresh state
          // This ensures we get the latest from the server
          const refreshResponse = await fetch(AMAZING_API_URL);
          if (refreshResponse.ok) {
            const refreshData = await refreshResponse.json();
            setItems(refreshData.items);
          }
        }
        
        setNewItemText("");
        setIsConnected(true); // Mark as connected since POST worked
        // Focus back to textarea
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      } else if (response.status === 400) {
        // Handle 400 errors (like language detection failures)
        try {
          const errorData = await response.json();
          setError(errorData.detail || 'Bad request');
        } catch {
          setError('Language could not be detected. Please try with text in a recognizable language.');
        }
        setIsConnected(true); // We are connected, just got a validation error
      } else {
        throw new Error('API not available');
      }
    } catch (error) {
      console.error('Error creating amazing item:', error);
      // Fallback: Add item locally when API is not available
      const newItem: AmazingItem = {
        id: Date.now().toString(),
        text: newItemText.trim(),
        language: "Auto-detected", // Placeholder for offline mode
        reps: 1,
      };
      setItems(prev => [...prev, newItem]);
      setNewItemText("");
      setIsConnected(false);
      
      // Focus back to textarea
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveList = () => {
    // Create text content with one item per line
    const textContent = items.map(item => 
      `${item.text} (${item.language}) - ${item.reps} ${item.reps === 1 ? 'time' : 'times'}`
    ).join('\n');
    
    // Create and download the file
    const blob = new Blob([textContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `amazing-list-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">You are amazing!</h1>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              {isConnected ? (
                <div className="flex items-center gap-1 text-green-600 text-sm">
                  <Wifi className="h-4 w-4" />
                  <span>Live updates active</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-red-600 text-sm">
                  <WifiOff className="h-4 w-4" />
                  <span>Connecting...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Add New Item Form */}
        <Card>
          <CardHeader>
            <CardTitle>Write &quot;You are amazing&quot; in your mother tongue</CardTitle>
            <p className="text-sm text-gray-600">Language will be automatically detected by AI</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-700">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">{error}</span>
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="message">Your amazing message</Label>
                <Textarea
                  id="message"
                  ref={textareaRef}
                  placeholder="Write 'You are amazing' in your language..."
                  value={newItemText}
                  onChange={(e) => {
                    setNewItemText(e.target.value);
                    if (error) setError(null); // Clear error when user types
                  }}
                  className="min-h-[100px] resize-none"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                      handleSubmit(e);
                    }
                  }}
                />
              </div>
              <div className="flex justify-between items-center">
                <p className="text-sm text-gray-500">
                  Press Cmd+Enter (Mac) or Ctrl+Enter (Windows) to submit
                </p>
                <Button 
                  type="submit" 
                  disabled={!newItemText.trim() || isSubmitting}
                  className="flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  {isSubmitting ? "Adding..." : "Add Item"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Amazing Items List */}
        <Card>
          <CardContent className="space-y-4">
            {items.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No items yet. Add one above to get started!</p>
              </div>
            ) : (
              items.map((item) => (
                <div key={item.id}>
                  <div className="flex items-start gap-4 p-4 rounded-lg bg-white border border-gray-200 hover:border-gray-300 transition-all duration-200">
                    <div className="flex-1 min-w-0">
                      <p className="text-gray-900 text-lg font-medium">{item.text}</p>
                      <div className="flex items-center gap-4 mt-1">
                        <p className="text-gray-500 text-sm">{item.language}</p>
                        <span className="text-gray-400">•</span>
                        <p className="text-blue-600 text-sm font-medium">
                          {item.reps} {item.reps === 1 ? 'time' : 'times'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Stats and Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <Clock className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{items.length}</p>
                  <p className="text-gray-600 text-sm">Total Items</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <Button
                onClick={handleSaveList}
                variant="outline"
                className="w-full flex items-center gap-2"
                disabled={items.length === 0}
              >
                <Download className="h-4 w-4" />
                Save the list
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
