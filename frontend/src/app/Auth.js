"use client";

import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
export default function Auth() {
  const [S_email, setS_Email] = useState("");
  const [S_password, setS_Password] = useState("");
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [accessToken, setAccessToken] = useState(() =>
    localStorage.getItem("access_token")
  ); // Add state for storing the access token
  const handleLogin = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log(data);
        setAccessToken(data.access_token);
        localStorage.setItem("access_token", data.access_token);
        window.location.href = "/main";
      } else {
        // Handle unsuccessful login, display an error message, etc.
        console.error("Login failed");
      }
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  const handleSignup = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: S_email,
          password: S_password,
        }),
      });

      if (response.ok) {
        toast({
          description: "The portal is now open 🚪✨ login now !!",
        });
      } else {
        // Handle unsuccessful login, display an error message, etc.
        console.error("signup failed");
      }
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  return (
    <main className="flex h-screen w-screen">
      <div className="font-rubik pl-8 pt-6 font-semibold absolute transform -translate-x-1/6 -translate-y-1/6 z-10">
        <div className=" text-black text-8xl ">HashGPT</div>
        <p className=" pl-12 text-black font-normal text-2xl">
          {" "}
          Spark Conversations with Your Blog! 💬✨
        </p>
      </div>

      <div className="relative  w-1/2">
        <Image
          src="/ReadingSideDoodle.svg"
          width={350} // Adjust the width as needed
          height={350} // Adjust the height as needed
          alt="Reading Side Doodle"
          className="absolute bottom-4 pl-4"
        />
      </div>

      {/* Right side: Tabs */}
      <div className="flex-grow  pt-16">
        <Tabs defaultValue="Login" className="w-[400px]">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="Sign up">Sign up</TabsTrigger>
            <TabsTrigger value="Login">Login</TabsTrigger>
          </TabsList>
          <TabsContent value="Sign up">
            <Card>
              <CardContent className="space-y-2 pt-4">
                <div className="space-y-1">
                  <Label htmlFor="Email">Email</Label>
                  <Input
                    id="Email"
                    value={S_email}
                    onChange={(e) => setS_Email(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="Password">Password</Label>
                  <Input
                    id="Password"
                    value={S_password}
                    onChange={(e) => setS_Password(e.target.value)}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full" onClick={handleSignup}>
                  Sign up
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
          <TabsContent value="Login">
            <Card>
              <CardContent className="space-y-2 pt-4">
                <div className="space-y-1">
                  <Label htmlFor="Email">Email</Label>
                  <Input
                    id="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="Password">Password</Label>
                  <Input
                    id="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full" onClick={handleLogin}>
                  Login
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
