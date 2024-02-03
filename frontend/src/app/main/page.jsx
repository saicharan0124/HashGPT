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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
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
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [typedAnswer, setTypedAnswer] = useState('');
    const [accessToken, setAccessToken] = useState('');
    const [url, setUrl] = useState('');
    const { toast } = useToast();

    useEffect(() => {
        // Retrieve access token from local storage during component initialization
        const storedAccessToken = localStorage.getItem('access_token');
        if (storedAccessToken) {
            setAccessToken(storedAccessToken);
        }
    }, []);

    const handleAddUrl = async () => {
        try {
            // Assuming you have the access token stored in localStorage
            const storedAccessToken = localStorage.getItem('access_token');
            if (storedAccessToken) {
                setAccessToken(storedAccessToken);
            } else {
                // Handle the case where the access token is not available
                console.error('Access token not found');
                return;
            }

            const response = await fetch('http://127.0.0.1:8000/api/core/add_document', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({
                    url: url,
                }),
            });

            if (response.ok) {
                // Handle success, e.g., display a success message
                console.log('URL added successfully');
                toast({
                    description: "Boom! 🚀 Your blog has been seamlessly added! 🌟✨",

                });
            } else {
                // Handle failure, e.g., display an error message
                console.error('Failed to add URL');
            }
        } catch (error) {
            console.error('Error during /api/core/add_document request:', error);
        }
    };

    const handleAskQuestion = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/core/answergen', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: JSON.stringify({
                    query: question,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                const firstAnswer = data?.response?.answers?.[0]?.answer || 'No answer available';
                setAnswer(firstAnswer);
                typeAnswer(firstAnswer);
                // Do something with the answer if needed
                console.log('Answer:', firstAnswer);
                // Do something with the answer if needed
                console.log('Answer:', data.answer);
            } else {
                console.error('Failed to get answer');
            }
        } catch (error) {
            console.error('Error during /api/core/answergen request:', error);
        }
    };

    const typeAnswer = (text) => {
        let index = 0;
        const intervalId = setInterval(() => {
            setTypedAnswer((prevTyped) => prevTyped + text[index]);
            index += 1;
            if (index === text.length) {
                clearInterval(intervalId);
            }
        }, 30); // Adjust the interval as needed
    };
    return (
        <div className="flex items-center justify-center h-screen">
            <div className="fixed top-0 flex  justify-between pr-6 w-full z-50">
                <div className="flex items-center">
                    <span className="text-5xl font-rubik font-semibold ml-4 mr-10">HashGPT</span>
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

            <Tabs defaultValue="Add" className="w-[400px]">
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="Add">Embed 🛠️</TabsTrigger>
                    <TabsTrigger value="Query">Engage 💬</TabsTrigger>
                </TabsList>
                <TabsContent value="Add">
                    <Card>
                        <CardHeader>
                            <CardTitle>Embed.</CardTitle>
                            <CardDescription>
                                Ready to roll! 🚀 Add the URL of the blog you want to query and let the magic begin! ✨🔍
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <div className="space-y-2 flex flex-col  items-center">
                                <Label htmlFor="url">Input url</Label>
                                <Input id="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://blog.developerdao.com/uploading-files-to-arweave-with-irys" />
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button className="w-full" onClick={() => {
                                handleAddUrl()
                                toast({
                                    description: "Processing might take a bit, but I'll give you a heads-up once it's completed! 🤖✨",
                                })
                            }}>Infuse</Button>
                        </CardFooter>
                    </Card>
                </TabsContent>
                <TabsContent value="Query">
                    <Card>
                        <CardHeader>
                            <CardTitle>Engage </CardTitle>
                            <CardDescription>
                                Engage with your curated blogs! 🗣️💬
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <div className="space-y-1">
                                <Label htmlFor="Question">Question</Label>
                                <Textarea placeholder="Type your question here." value={question}
                                    onChange={(e) => setQuestion(e.target.value)} />
                            </div>

                        </CardContent>
                        <CardFooter>
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button className="w-full" onClick={handleAskQuestion} disabled={!accessToken}>Inquire</Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>Answer from ur document</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            {typedAnswer}
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>ok!</AlertDialogCancel>

                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        </CardFooter>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
