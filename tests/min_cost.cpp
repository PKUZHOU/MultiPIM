#include<iostream>
#include<algorithm>
#include<vector>
#include<queue>
#include<fstream>
#include<memory.h>
#include<string>
#define N 1005
#define M 1000100
#define INF 10000000
using namespace std;
struct edge {
	int next,to,v,from,f;
}e[M];
int tot,head[N],dis[N],pre[N];
int ans,n,m,S,T;
bool vis[N];
void add(int u,int v,int w,int f) {
	e[tot]=(edge){head[u],v,w,u,f};
	head[u]=tot++;
	e[tot]=(edge){head[v],u,0,v,-f};
	head[v]=tot++;
}
bool spfa() {
	memset(dis,0x3f,sizeof(dis));
	memset(vis,0,sizeof(vis));
	queue<int>q;
	q.push(S);
	dis[S]=0;
	while(!q.empty()) {
		int now=q.front();
		q.pop();
		vis[now]=0;
		for(int i=head[now];i!=-1;i=e[i].next)
			if(e[i].v&&dis[e[i].to]>dis[now]+e[i].f) {
				dis[e[i].to]=dis[now]+e[i].f;
				pre[e[i].to]=i;
				if(!vis[e[i].to])
				vis[e[i].to]=1,q.push(e[i].to);
			}
	}
	return dis[T]<INF;
}
void end() {
	int t=INF;
	for(int i=T;i!=S;i=e[pre[i]].from) {
		t=min(t,e[pre[i]].v);
	}
	for(int i=T;i!=S;i=e[pre[i]].from) {
		e[pre[i]].v-=t,e[pre[i]^1].v+=t;
	}
	ans+=dis[T]*t;
}



int main() 
{
	string in_file_name, out_file_name;
	cin >> in_file_name >> out_file_name;
	ifstream in_file(in_file_name.c_str());
	ofstream out_file(out_file_name.c_str());
	
	memset(head,-1,sizeof(head));
	in_file >> n >> m;
	S=n+m+1;
	T=n+m+2;
	for(int i=1;i<=m;i++)
		add(S,i,1,0);
	for(int i=1;i<=n;i++)
		add(m+i,T,4,0);
	for(int i=1;i<=n;i++) 
	{
		for(int j=1;j<=m;j++) 
		{
			int x;
			in_file >> x;
			add(j,m+i,1,x);
		}
	}
	while(spfa())end();
	printf("Answer is %d\n",ans);
	
	for(int i=1;i<=m;i++) 
	{
		for(int j=head[i];j!=-1;j=e[j].next) 
		{
			if((j^1)&&e[j].v==0) 
			{
				printf("%d %d\n",i-1, e[j].to-m-1);
				out_file << i-1 << " " << e[j].to-m-1;
				out_file << "\n";
			}
		}
	}
}
