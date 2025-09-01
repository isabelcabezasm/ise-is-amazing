"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2, Download, ArrowLeft, FileText } from "lucide-react";
import Link from "next/link";
import { API_BASE_URL, AMAZING_API_URL } from "@/lib/api-config";

const COLORMAP_OPTIONS = [
  { value: "viridis", label: "Viridis" },
  { value: "plasma", label: "Plasma" },
  { value: "rainbow", label: "Rainbow" },
  { value: "cool", label: "Cool" },
  { value: "hot", label: "Hot" },
  { value: "spring", label: "Spring" },
  { value: "summer", label: "Summer" },
  { value: "autumn", label: "Autumn" },
  { value: "winter", label: "Winter" },
];

const BACKGROUND_COLORS = [
  { value: "white", label: "White" },
  { value: "black", label: "Black" },
  { value: "navy", label: "Navy" },
  { value: "darkblue", label: "Dark Blue" },
  { value: "darkgreen", label: "Dark Green" },
  { value: "maroon", label: "Maroon" },
];

interface AmazingItem {
  id: string;
  text: string;
  language: string;
  reps: number;
}

export default function WordCloudPage() {
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [width, setWidth] = useState("800");
  const [height, setHeight] = useState("400");
  const [backgroundColor, setBackgroundColor] = useState("white");
  const [colormap, setColormap] = useState("viridis");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [amazingItems, setAmazingItems] = useState<AmazingItem[]>([]);
  const [loadingAmazing, setLoadingAmazing] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadError(null);

    try {
      const text = await file.text();
      const lines = text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

      if (lines.length === 0) {
        setUploadError("File is empty or contains no valid sentences.");
        return;
      }

      // Parse lines to extract text, language, and repetitions
      const items = lines.map(line => {
        // Try to extract language and reps from patterns like "(English) - 3 times"
        const languageMatch = line.match(/\(([^)]+)\)/);
        const repsMatch = line.match(/(\d+)\s*(time|times)/i);
        
        // Clean line by removing language and reps info
        const cleanLine = line.replace(/\s*\([^)]+\)\s*-\s*\d+\s*(time|times)\s*$/i, '').trim();
        
        return {
          text: cleanLine,
          language: languageMatch ? languageMatch[1] : "Auto-detected",
          reps: repsMatch ? parseInt(repsMatch[1]) : 1
        };
      }).filter(item => item.text.length > 0);

      if (items.length === 0) {
        setUploadError("No valid sentences found in the file.");
        return;
      }

      // Call the enhanced batch API endpoint
      const response = await fetch(`${API_BASE_URL}/api/amazing/batch-enhanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items: items
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Refresh the amazing items list from the API
      await fetchAmazingItems();
      
      // Show success message
      if (result.skipped_duplicates > 0) {
        console.log(`Added ${result.added_items.length} new items, updated ${result.skipped_duplicates} existing items with additional repetitions`);
      } else {
        console.log(`Added ${result.added_items.length} new items`);
      }
      
      // Clear the file input
      event.target.value = '';
      
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError("Error uploading file. Please try again.");
    }
  };

  const generateWordCloud = async () => {
    setLoadingAmazing(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/cloud/amazing?width=${width}&height=${height}&background_color=${backgroundColor}&colormap=${colormap}`
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
      } else {
        alert("Failed to generate word cloud");
      }
    } catch (error) {
      console.error("Error generating word cloud:", error);
      alert("Error generating word cloud");
    } finally {
      setLoadingAmazing(false);
    }
  };

  const fetchAmazingItems = async () => {
    try {
      const response = await fetch(AMAZING_API_URL);
      if (response.ok) {
        const data = await response.json();
        setAmazingItems(data.items);
      }
    } catch (error) {
      console.error("Error fetching amazing items:", error);
    }
  };

  const downloadImage = () => {
    if (imageUrl) {
      const a = document.createElement("a");
      a.href = imageUrl;
      a.download = "sentence_cloud.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-4 mb-4">
            <Link
              href="/amazing"
              className="inline-flex items-center gap-1 text-gray-600 hover:text-gray-800 text-sm font-medium transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Amazing</span>
            </Link>
          </div>
          <h1 className="text-4xl font-bold text-gray-900">Word Cloud Generator</h1>
          <p className="text-lg text-gray-600">
            Create beautiful sentence clouds from your custom sentences, uploaded files, or amazing items
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Left Column - Configuration */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upload Sentences</CardTitle>
                <CardDescription>
                  Upload a file with sentences to add them to your amazing items
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* File Upload Section */}
                <div className="space-y-2">
                  <Label htmlFor="file-upload">Upload sentences from file</Label>
                  <div className="flex gap-2">
                    <Input
                      id="file-upload"
                      type="file"
                      accept=".txt,.csv"
                      onChange={handleFileUpload}
                      className="cursor-pointer"
                    />
                    <Button variant="outline" size="icon" title="Upload file">
                      <FileText className="h-4 w-4" />
                    </Button>
                  </div>
                  {uploadError && (
                    <p className="text-sm text-red-600">{uploadError}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    Upload a .txt file with one sentence per line. Compatible with files exported from the Amazing page.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Amazing Items Word Cloud</CardTitle>
                <CardDescription>
                  Generate a word cloud from all your amazing items
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={fetchAmazingItems} variant="outline" className="w-full">
                  Refresh Amazing Items ({amazingItems.length})
                </Button>

                <Button
                  onClick={generateWordCloud}
                  disabled={loadingAmazing}
                  className="w-full"
                >
                  {loadingAmazing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    "Generate Amazing Cloud"
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Customization</CardTitle>
                <CardDescription>Customize your word cloud appearance</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="width">Width</Label>
                    <Input
                      id="width"
                      type="number"
                      value={width}
                      onChange={(e) => setWidth(e.target.value)}
                      min="400"
                      max="1200"
                    />
                  </div>
                  <div>
                    <Label htmlFor="height">Height</Label>
                    <Input
                      id="height"
                      type="number"
                      value={height}
                      onChange={(e) => setHeight(e.target.value)}
                      min="200"
                      max="800"
                    />
                  </div>
                </div>

                <div>
                  <Label>Background Color</Label>
                  <Select value={backgroundColor} onValueChange={setBackgroundColor}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {BACKGROUND_COLORS.map((color) => (
                        <SelectItem key={color.value} value={color.value}>
                          {color.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Color Map</Label>
                  <Select value={colormap} onValueChange={setColormap}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {COLORMAP_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Generated Word Cloud */}
          <div className="space-y-6">
            <Card className="h-fit">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Generated Cloud
                  {imageUrl && (
                    <Button onClick={downloadImage} size="sm" variant="outline">
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  )}
                </CardTitle>
                <CardDescription>
                  Your sentence cloud or word cloud will appear here after generation
                </CardDescription>
              </CardHeader>
              <CardContent>
                {imageUrl ? (
                  <div className="border rounded-lg overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={imageUrl}
                      alt="Generated Word Cloud"
                      className="w-full h-auto"
                    />
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg h-64 flex items-center justify-center">
                    <div className="text-center space-y-2">
                      <div className="text-muted-foreground">No word cloud generated yet</div>
                      <div className="text-sm text-muted-foreground">
                        Click one of the generate buttons to create your word cloud
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {amazingItems.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Amazing Items Preview</CardTitle>
                  <CardDescription>
                    Items that will be used in the amazing word cloud
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {amazingItems.map((item) => (
                      <div key={item.id} className="flex justify-between items-center">
                        <span className="text-sm">{item.text}</span>
                        <div className="flex gap-2">
                          <Badge variant="outline">{item.language}</Badge>
                          <Badge variant="secondary">×{item.reps}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm py-8">
          <p>Create beautiful word clouds with amazing messages 🌟</p>
        </div>
      </div>
    </div>
  );
}
