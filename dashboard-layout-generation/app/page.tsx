import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { Header } from "@/components/dashboard/header"
import { MeetingFeed } from "@/components/dashboard/meeting-feed"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"

export default function DashboardPage() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-background">
        <Header />
        <main className="flex-1 p-6 overflow-auto">
          <MeetingFeed />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
