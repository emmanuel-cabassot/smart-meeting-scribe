"use client"

import { Home, Upload, Star, Users, Briefcase, Calendar, Folder, Settings } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ChevronRight } from "lucide-react"

const workspaceItems = [
  { icon: Home, label: "My Feed", active: true },
  { icon: Upload, label: "Uploads", active: false },
  { icon: Star, label: "Favorites", active: false },
]

const groups = [
  {
    name: "Departments",
    icon: Users,
    items: ["R&D", "Marketing", "Direction"],
  },
  {
    name: "Projects",
    icon: Briefcase,
    items: ["V5 Launch", "Audit"],
  },
  {
    name: "Recurring",
    icon: Calendar,
    items: ["COMOP", "Daily"],
  },
]

export function AppSidebar() {
  return (
    <Sidebar className="border-sidebar-border">
      <SidebarHeader className="px-4 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600">
            <span className="text-sm font-bold text-white">S</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground">Smart Scribe</h1>
            <span className="text-[10px] text-muted-foreground">v6.0</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-[10px] uppercase tracking-wider text-muted-foreground">
            My Workspace
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {workspaceItems.map((item) => (
                <SidebarMenuItem key={item.label}>
                  <SidebarMenuButton
                    isActive={item.active}
                    tooltip={item.label}
                    className={item.active ? "bg-primary/10 text-primary" : ""}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                    {item.active && (
                      <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />
                    )}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Groups
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {groups.map((group) => (
                <Collapsible key={group.name} defaultOpen={group.name === "Departments"} className="group/collapsible">
                  <SidebarMenuItem>
                    <CollapsibleTrigger asChild>
                      <SidebarMenuButton tooltip={group.name}>
                        <group.icon className="h-4 w-4" />
                        <span>{group.name}</span>
                        <ChevronRight className="ml-auto h-4 w-4 transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                      </SidebarMenuButton>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      <SidebarMenuSub>
                        {group.items.map((item) => (
                          <SidebarMenuSubItem key={item}>
                            <SidebarMenuSubButton asChild>
                              <a href="#">
                                <Folder className="h-3.5 w-3.5" />
                                <span>{item}</span>
                              </a>
                            </SidebarMenuSubButton>
                          </SidebarMenuSubItem>
                        ))}
                      </SidebarMenuSub>
                    </CollapsibleContent>
                  </SidebarMenuItem>
                </Collapsible>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-3">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton className="w-full">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-gradient-to-br from-violet-500 to-indigo-600 text-xs font-medium text-white">
                  EC
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-1 flex-col items-start">
                <span className="text-sm font-medium text-foreground">Emmanuel C.</span>
                <span className="text-[10px] text-muted-foreground">Pro Plan</span>
              </div>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
