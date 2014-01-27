//
//  MainFlipsideViewController.m
//  Nightcoin
//
//  Created by Nightcoin Developers on 1/22/14.
//  Copyright (c) 2014 Nightmarket.org. All rights reserved.
//

#import "MainFlipsideViewController.h"
#import <Firebase/Firebase.h>

@interface MainFlipsideViewController ()

@end

@implementation MainFlipsideViewController

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    [self loaddebuginfo];
    
    timer_sync = [NSTimer scheduledTimerWithTimeInterval:3 target:self selector:@selector(loaddebuginfo) userInfo:nil repeats:YES];
    
}
    
- (void)loaddebuginfo{
    debuginfoloaded=false;
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    Firebase* f = [[Firebase alloc] initWithUrl:[NSString stringWithFormat:@"https://nightmarket.firebaseIO.com/iOS_users/%@",[defaults objectForKey:@"uid"]]];
    
    // Read data and react to changes
    [f observeSingleEventOfType:FEventTypeValue withBlock:^(FDataSnapshot *snapshot) {
        debuginfo.text = [snapshot description];
        debuginfoloaded=true;
    }];
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

#pragma mark - Actions

- (IBAction)done:(id)sender
{
    [timer_sync invalidate];
    if (debuginfoloaded) {
        [self.delegate flipsideViewControllerDidFinish:self];
    }
}

@end
