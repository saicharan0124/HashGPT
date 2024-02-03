"use client";
import Link from "next/link";
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    Sheet,
    SheetClose,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger,
} from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { useState, useEffect } from "react";
import { useToast } from "@/components/ui/use-toast";
import {
    AlertDialog,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"

export default function page() {
    const { toast } = useToast()
    const [hostname, sethostname] = useState('');
    const [api_key, setapi_key] = useState('');
    const [accessToken, setAccessToken] = useState('');
    
    useEffect(() => {
        // Retrieve access token from local storage during component initialization
        const storedAccessToken = localStorage.getItem('access_token');
        if (storedAccessToken) {
            setAccessToken(storedAccessToken);
        }
    }, []);

    const handlereplyrover = async () => {
        try {
            const storedAccessToken = localStorage.getItem('access_token');
            setAccessToken(storedAccessToken);
            const response = await fetch('http://127.0.0.1:8000/api/core/replyrover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({
                    host: hostname,
                    api_key: api_key 
                }),
            });

            if (response.ok) {
                toast({
                    description: "Reply Rover AI at your service! 🚀💬",

                });

            } else {
                console.error('Failed to get answer');
            }
        } catch (error) {
            console.error('Error during /api/core/answergen request:', error);
        }
    };
    return (
        <div>
            <div className="fixed top-0 flex justify-between  pr-6 w-full z-50">
                <div className="flex items-center">
                    <span className="text-5xl font-rubik  font-semibold ml-4 mr-10">HashGPT</span>
                    {/* Add any additional elements or styling as needed */}
                </div>
                <NavigationMenu>
                    <NavigationMenuList >
                        <NavigationMenuItem >
                            <Link href="/replyrover" legacyBehavior passHref>
                                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                                    ReplyRoverAI
                                </NavigationMenuLink>
                            </Link>
                        </NavigationMenuItem>

                        {/* Documentation Link */}
                        <NavigationMenuItem>
                            <Link href="/main" legacyBehavior passHref>
                                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                                    BlogConverse
                                </NavigationMenuLink>
                            </Link>
                        </NavigationMenuItem>
                    </NavigationMenuList>
                </NavigationMenu>
            </div>
            <div className="flex items-center justify-center h-screen">
                <Card className="w-[400px]">
                    <CardHeader>
                        <CardTitle>ReplyRover AI</CardTitle>
                        <CardDescription> Set your own Blog Agent: Your Comment Concierge! 🌟 </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form>
                            <div className="grid w-full items-center gap-4">
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="name">Blog Name</Label>
                                    <Input
                                        id="name"
                                        value={hostname}
                                        onChange={(e) => sethostname(e.target.value)}
                                        placeholder="blog.developerdao.com" />
                                </div>
                                <div className="flex flex-col space-y-1">
                                    <Label htmlFor="apikey">API Key</Label>
                                    <Input
                                        id="apikey"
                                        value={api_key}
                                        onChange={(e) => setapi_key(e.target.value)} />

                                </div>
                            </div>
                        </form>
                    </CardContent>
                    <CardFooter className="flex justify-between">

                        <Button className="w-full" onClick={() => {
                            handlereplyrover()
                            toast({
                                description: "Processing might take a bit, but I'll give you a heads-up once it's completed! 🤖✨",
                            })
                        }}>Deploy</Button>
                    </CardFooter>
                </Card>
            </div>

        </div>)
}