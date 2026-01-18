"use client"

import React from "react"

import { useState, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import {
  ArrowLeft,
  Upload,
  CloudUpload,
  X,
  File,
  Building2,
  FolderKanban,
  Calendar,
} from "lucide-react"

type UploadState = "idle" | "selected" | "uploading" | "success"

interface Group {
  id: string
  name: string
  type: "department" | "project" | "recurring"
}

const GROUPS: Group[] = [
  { id: "tous", name: "Tous", type: "department" },
  { id: "rd", name: "R&D", type: "department" },
  { id: "marketing", name: "Marketing", type: "department" },
  { id: "v5-launch", name: "V5 Launch", type: "project" },
  { id: "audit", name: "Audit", type: "project" },
  { id: "comop", name: "COMOP", type: "recurring" },
  { id: "daily", name: "Daily", type: "recurring" },
]

const ACCEPTED_FORMATS = ["audio/mp3", "audio/mpeg", "audio/wav", "audio/x-wav", "audio/m4a", "audio/x-m4a", "video/mp4", "video/webm"]
const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024 // 2GB

function getGroupIcon(type: Group["type"]) {
  switch (type) {
    case "department":
      return <Building2 className="h-4 w-4" />
    case "project":
      return <FolderKanban className="h-4 w-4" />
    case "recurring":
      return <Calendar className="h-4 w-4" />
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes"
  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`
}

export default function UploadPage() {
  const [uploadState, setUploadState] = useState<UploadState>("idle")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [meetingTitle, setMeetingTitle] = useState("")
  const [selectedGroups, setSelectedGroups] = useState<string[]>([])
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isDragOver, setIsDragOver] = useState(false)
  const [showGroupError, setShowGroupError] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }, [])

  const handleFileSelect = (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      alert("File size exceeds 2GB limit")
      return
    }
    setSelectedFile(file)
    setUploadState("selected")
    setShowGroupError(false)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setUploadState("idle")
    setShowGroupError(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleGroupToggle = (groupId: string) => {
    setSelectedGroups((prev) =>
      prev.includes(groupId)
        ? prev.filter((id) => id !== groupId)
        : [...prev, groupId]
    )
    setShowGroupError(false)
  }

  const handleUpload = () => {
    if (selectedGroups.length === 0) {
      setShowGroupError(true)
      return
    }

    setUploadState("uploading")
    // Simulate upload progress
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 15
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        setTimeout(() => {
          setUploadState("success")
        }, 500)
      }
      setUploadProgress(progress)
    }, 300)
  }

  const handleCancel = () => {
    setUploadState("selected")
    setUploadProgress(0)
  }

  const groupsByType = {
    department: GROUPS.filter((g) => g.type === "department"),
    project: GROUPS.filter((g) => g.type === "project"),
    recurring: GROUPS.filter((g) => g.type === "recurring"),
  }

  const isFormValid = selectedFile && selectedGroups.length > 0

  if (uploadState === "success") {
    return (
      <main className="min-h-screen bg-[#0a0a0b] flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mx-auto">
            <CloudUpload className="h-8 w-8 text-primary" />
          </div>
          <h2 className="text-2xl font-semibold text-foreground">Upload Complete!</h2>
          <p className="text-muted-foreground">
            Your meeting is being processed. You will be redirected shortly...
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#0a0a0b] p-4 md:p-8">
      <div className="max-w-[600px] mx-auto space-y-6">
        {/* Back Button */}
        <Button
          variant="ghost"
          className="text-muted-foreground hover:text-foreground hover:bg-muted/50 -ml-2"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        {/* Page Title */}
        <h1 className="text-2xl md:text-3xl font-semibold text-foreground">
          Upload New Meeting
        </h1>

        {/* Drag & Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            relative rounded-xl border-2 border-dashed p-8 md:p-12 text-center cursor-pointer
            transition-all duration-300 ease-out
            backdrop-blur-sm bg-card/30
            ${
              isDragOver
                ? "border-primary bg-primary/10 scale-[1.02]"
                : "border-border/50 hover:border-primary/50 hover:bg-muted/30"
            }
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp3,.wav,.m4a,.mp4,.webm"
            onChange={handleFileInputChange}
            className="sr-only"
          />
          
          {!selectedFile ? (
            <div className="space-y-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                <CloudUpload className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-foreground font-medium">
                  Drag & drop your audio or video file here
                </p>
                <p className="text-muted-foreground text-sm mt-1">
                  or click to browse
                </p>
              </div>
              <div className="text-xs text-muted-foreground space-y-1">
                <p>Accepted formats: MP3, WAV, M4A, MP4, WEBM</p>
                <p>Max size: 2GB</p>
              </div>
            </div>
          ) : (
            <div
              className="flex items-center justify-between gap-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <File className="h-5 w-5 text-primary" />
                </div>
                <div className="min-w-0 text-left">
                  <p className="text-foreground font-medium truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-muted-foreground text-sm">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRemoveFile}
                className="flex-shrink-0 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Form Fields - Only show when file is selected */}
        {selectedFile && uploadState !== "uploading" && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            {/* Title Input */}
            <div className="space-y-2">
              <Label htmlFor="title" className="text-foreground">
                Meeting Title <span className="text-muted-foreground">(optional)</span>
              </Label>
              <Input
                id="title"
                placeholder="Will use filename if empty"
                value={meetingTitle}
                onChange={(e) => setMeetingTitle(e.target.value)}
                className="bg-card/30 border-border/50 focus:border-primary placeholder:text-muted-foreground/50"
              />
            </div>

            {/* Group Selection */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Label className="text-foreground">Select Groups</Label>
                <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary font-medium">
                  Required
                </span>
              </div>
              
              <div className="rounded-xl border border-border/50 bg-card/30 backdrop-blur-sm p-4 space-y-4">
                {/* Departments */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Departments
                  </p>
                  <div className="space-y-2">
                    {groupsByType.department.map((group) => (
                      <label
                        key={group.id}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/30 cursor-pointer transition-colors"
                      >
                        <Checkbox
                          checked={selectedGroups.includes(group.id)}
                          onCheckedChange={() => handleGroupToggle(group.id)}
                          className="border-border data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                        />
                        <div className="flex items-center gap-2 text-foreground">
                          {getGroupIcon(group.type)}
                          <span>{group.name}</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Projects */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Projects
                  </p>
                  <div className="space-y-2">
                    {groupsByType.project.map((group) => (
                      <label
                        key={group.id}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/30 cursor-pointer transition-colors"
                      >
                        <Checkbox
                          checked={selectedGroups.includes(group.id)}
                          onCheckedChange={() => handleGroupToggle(group.id)}
                          className="border-border data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                        />
                        <div className="flex items-center gap-2 text-foreground">
                          {getGroupIcon(group.type)}
                          <span>{group.name}</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Recurring */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Recurring
                  </p>
                  <div className="space-y-2">
                    {groupsByType.recurring.map((group) => (
                      <label
                        key={group.id}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/30 cursor-pointer transition-colors"
                      >
                        <Checkbox
                          checked={selectedGroups.includes(group.id)}
                          onCheckedChange={() => handleGroupToggle(group.id)}
                          className="border-border data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                        />
                        <div className="flex items-center gap-2 text-foreground">
                          {getGroupIcon(group.type)}
                          <span>{group.name}</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              {showGroupError && (
                <p className="text-destructive text-sm animate-in fade-in slide-in-from-top-1">
                  Please select at least one group
                </p>
              )}
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {uploadState === "uploading" && (
          <div className="rounded-xl border border-border/50 bg-card/30 backdrop-blur-sm p-6 space-y-4 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Upload className="h-5 w-5 text-primary animate-pulse" />
                </div>
                <div className="min-w-0">
                  <p className="text-foreground font-medium truncate">
                    {selectedFile?.name}
                  </p>
                  <p className="text-muted-foreground text-sm">
                    Uploading... {Math.round(uploadProgress)}%
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCancel}
                className="text-muted-foreground hover:text-destructive"
              >
                Cancel
              </Button>
            </div>
            <Progress value={uploadProgress} className="h-2 bg-muted" />
          </div>
        )}

        {/* Action Buttons */}
        {uploadState !== "uploading" && (
          <div className="flex items-center justify-between pt-4">
            <Button
              variant="ghost"
              className="text-muted-foreground hover:text-foreground"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!isFormValid}
              className="bg-primary hover:bg-primary/90 text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Upload className="h-4 w-4 mr-2" />
              Upload & Process
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}
