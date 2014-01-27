//
//  MainFlipsideViewController.h
//  Nightcoin
//
//  Created by Nightcoin Developers on 1/22/14.
//  Copyright (c) 2014 Nightmarket.org. All rights reserved.
//

#import <UIKit/UIKit.h>

@class MainFlipsideViewController;

@protocol MainFlipsideViewControllerDelegate
- (void)flipsideViewControllerDidFinish:(MainFlipsideViewController *)controller;
@end

@interface MainFlipsideViewController : UIViewController{
    IBOutlet UILabel * debuginfo;
    bool debuginfoloaded;
    NSTimer * timer_sync;
}

@property (weak, nonatomic) id <MainFlipsideViewControllerDelegate> delegate;

- (IBAction)done:(id)sender;

@end
