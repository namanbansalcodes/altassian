import type {Space, User} from "@/lib/types";
import {Sidebar} from "./Sidebar";
import {TopBar} from "./TopBar";

export function Chrome({user, spaces, children}: {user: User; spaces: Space[]; children: React.ReactNode}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar spaces={spaces} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar user={user} />
        <main className="flex-1 overflow-auto bg-white">{children}</main>
      </div>
    </div>
  );
}
